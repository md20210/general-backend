#!/bin/bash
# =============================================================================
# General Backend - Deployment Script
# =============================================================================
# Deploys:
# 1. Backend to GitHub + Railway
# 2. Admin Frontend to Strato (/htdocs/admin/)
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config
SFTP_CREDENTIALS="/mnt/e/Project20250615/portfolio-website/michael-homepage/.env.sftp"
DEPLOY_GITHUB=true
DEPLOY_STRATO=true
SKIP_BUILD=false
DRY_RUN=false
ERRORS=0
WARNINGS=0
LOG_FILE="deployment-$(date +%Y%m%d-%H%M%S).log"

# Helper functions
log() { echo -e "${1}" | tee -a "$LOG_FILE"; }
error() { ((ERRORS++)); log "${RED}❌ ERROR: ${1}${NC}"; }
warning() { ((WARNINGS++)); log "${YELLOW}⚠️  WARNING: ${1}${NC}"; }
success() { log "${GREEN}✅ ${1}${NC}"; }
info() { log "${BLUE}ℹ️  ${1}${NC}"; }
section() {
    log "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${BLUE}  ${1}${NC}"
    log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

confirm() {
    if [ "$DRY_RUN" = true ]; then
        log "${YELLOW}[DRY RUN] Would ask: ${1}${NC}"
        return 0
    fi
    read -p "$(echo -e ${YELLOW}${1}${NC} [y/N]: )" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Load SFTP credentials
load_sftp_credentials() {
    if [ -f "$SFTP_CREDENTIALS" ]; then
        source "$SFTP_CREDENTIALS"
        success "SFTP credentials loaded"
    else
        error "SFTP credentials not found at: $SFTP_CREDENTIALS"
        return 1
    fi
}

# Build admin frontend
build_admin_frontend() {
    section "Building Admin Frontend"

    if [ "$SKIP_BUILD" = true ]; then
        warning "Skipping build (--skip-build flag)"
        return 0
    fi

    cd admin-frontend

    info "Installing dependencies..."
    if npm install >> "../$LOG_FILE" 2>&1; then
        success "Dependencies installed"
    else
        error "npm install failed"
        cd ..
        return 1
    fi

    info "Building frontend..."
    if npm run build >> "../$LOG_FILE" 2>&1; then
        success "Frontend build completed"

        if [ -d "dist" ]; then
            local file_count=$(find dist -type f | wc -l)
            info "Build output: $file_count files in dist/"
        else
            error "dist/ folder not found after build"
            cd ..
            return 1
        fi

        # Create .htaccess for SPA routing
        info "Creating .htaccess for SPA routing..."
        cat > dist/.htaccess <<'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /admin/
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /admin/index.html [L]
</IfModule>
EOF
        success ".htaccess created"

        cd ..
        return 0
    else
        error "Frontend build failed"
        cd ..
        return 1
    fi
}

# Upload admin frontend to Strato
upload_admin_to_strato() {
    section "Uploading Admin Frontend to Strato"

    if [ "$DEPLOY_STRATO" != true ]; then
        warning "Skipping Strato upload (--no-strato flag)"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would upload admin frontend to Strato"
        return 0
    fi

    load_sftp_credentials || return 1

    cd admin-frontend/dist

    info "Uploading to /htdocs/admin/ via lftp..."

    # Use lftp for reliable mirroring
    lftp -c "
        set sftp:auto-confirm yes
        open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST
        mirror -R --delete --verbose . /htdocs/admin/
        bye
    " >> "../../$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        success "Admin frontend uploaded to Strato"
        cd ../..
        return 0
    else
        error "Upload failed (check $LOG_FILE)"
        cd ../..
        return 1
    fi
}

# Deploy backend to GitHub
deploy_backend_to_github() {
    section "Deploying Backend to GitHub"

    if [ "$DEPLOY_GITHUB" != true ]; then
        warning "Skipping GitHub deployment (--no-github flag)"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would deploy to GitHub"
        return 0
    fi

    # Check for changes
    if git diff-index --quiet HEAD -- && git diff --staged --quiet; then
        info "No changes to commit"
        return 0
    fi

    info "Changes detected:"
    git status --short

    if ! confirm "Commit and push these changes to GitHub?"; then
        warning "GitHub deployment cancelled by user"
        return 1
    fi

    # Stage changes
    info "Staging changes..."
    git add .

    # Create commit
    local commit_msg="Deployment update $(date +%Y-%m-%d\ %H:%M)

General Backend deployment:
- Backend: FastAPI with Auth, LLM Gateway, Documents & Projects
- Frontend: React Admin Panel
- Phase 1-3 completed

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

    if git commit -m "$commit_msg" >> "$LOG_FILE" 2>&1; then
        success "Commit created"
    else
        info "No changes to commit after staging"
        return 0
    fi

    # Push to GitHub
    info "Pushing to GitHub..."
    if git push origin main >> "$LOG_FILE" 2>&1; then
        success "Pushed to GitHub"
        info "Railway will auto-deploy from GitHub (check Railway dashboard)"
        return 0
    else
        error "Failed to push to GitHub"
        return 1
    fi
}

# Verification
verify_deployment() {
    section "Verification Phase"

    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would verify deployment"
        return 0
    fi

    # Verify Strato
    if [ "$DEPLOY_STRATO" = true ]; then
        info "Verifying: https://www.dabrock.info/admin"
        if curl -s --head "https://www.dabrock.info/admin" | head -1 | grep -qE "HTTP/[0-9.]+ (200|301|302)"; then
            success "Admin frontend accessible"
        else
            warning "Admin frontend not yet accessible"
        fi
    fi

    # Verify GitHub
    if [ "$DEPLOY_GITHUB" = true ]; then
        local local_commit=$(git rev-parse HEAD)
        local remote_commit=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

        if [ "$local_commit" = "$remote_commit" ]; then
            success "Git push verified (commit: ${local_commit:0:7})"
        else
            warning "Git push verification failed (may need to pull)"
        fi
    fi
}

# Main deployment
run_deployment() {
    section "🚀 Starting General Backend Deployment"

    info "Log file: $LOG_FILE"
    info "Timestamp: $(date)"

    if [ "$DRY_RUN" = true ]; then
        warning "DRY RUN MODE - No actual changes"
    fi

    # Pre-flight checks
    section "Pre-flight Checks"

    if ! command -v npm &> /dev/null; then
        error "npm not found"
        return 1
    fi

    if ! command -v git &> /dev/null; then
        error "git not found"
        return 1
    fi

    if [ "$DEPLOY_STRATO" = true ] && ! command -v lftp &> /dev/null; then
        error "lftp not found (required for Strato upload)"
        return 1
    fi

    if [ "$DEPLOY_STRATO" = true ] && [ ! -f "$SFTP_CREDENTIALS" ]; then
        error "SFTP credentials not found at: $SFTP_CREDENTIALS"
        return 1
    fi

    success "All pre-flight checks passed"

    # Build & Deploy
    build_admin_frontend || return 1
    upload_admin_to_strato || return 1
    deploy_backend_to_github || return 1
    verify_deployment || return 1

    # Summary
    section "📊 Deployment Summary"

    if [ $ERRORS -eq 0 ]; then
        success "Deployment completed successfully! 🎉"
    else
        error "Deployment completed with $ERRORS error(s)"
    fi

    if [ $WARNINGS -gt 0 ]; then
        warning "Total warnings: $WARNINGS"
    fi

    info "Full log: $LOG_FILE"

    # Test URLs
    log "\n${GREEN}🌐 Test Your Deployment:${NC}"
    log "   • Admin Frontend: https://www.dabrock.info/admin"
    log "   • Backend API: https://your-railway-url.railway.app"
    log "   • API Docs: https://your-railway-url.railway.app/docs"
    log "   • GitHub: https://github.com/YOUR_USERNAME/general-backend"
    log ""
    log "${YELLOW}⚠️  Next Steps:${NC}"
    log "   1. Create GitHub repository: gh repo create general-backend --public --source=. --push"
    log "   2. Deploy to Railway: railway init && railway add -d postgres && railway up"
    log "   3. Set environment variables on Railway (see DEPLOYMENT_STEPS.md)"
    log "   4. Create admin user (see DEPLOYMENT_STEPS.md)"

    return $ERRORS
}

# Show help
show_help() {
    cat << EOF
🚀 General Backend - Deployment Script

USAGE:
    ./deploy.sh [OPTIONS]

OPTIONS:
    --help, -h          Show this help
    --dry-run           Show what would be done
    --skip-build        Skip frontend build
    --no-strato         Skip Strato upload
    --no-github         Skip GitHub deployment

EXAMPLES:
    # Full deployment
    ./deploy.sh

    # Dry run
    ./deploy.sh --dry-run

    # Deploy only frontend to Strato
    ./deploy.sh --no-github

    # Deploy only to GitHub (no Strato)
    ./deploy.sh --no-strato

DEPLOYMENT TARGETS:
    ✓ Strato SFTP (www.dabrock.info/admin)
    ✓ GitHub (auto-triggers Railway deploy)
    ✓ Railway (backend API)

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h) show_help; exit 0 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --skip-build) SKIP_BUILD=true; shift ;;
        --no-strato) DEPLOY_STRATO=false; shift ;;
        --no-github) DEPLOY_GITHUB=false; shift ;;
        *) error "Unknown option: $1"; show_help; exit 1 ;;
    esac
done

# Main
main() {
    cd "$(dirname "$0")"

    log "${GREEN}"
    log "╔═══════════════════════════════════════════════════════════════╗"
    log "║                                                               ║"
    log "║          General Backend - Deployment Script                 ║"
    log "║                                                               ║"
    log "╚═══════════════════════════════════════════════════════════════╝"
    log "${NC}"

    if run_deployment; then
        exit 0
    else
        exit 1
    fi
}

main
