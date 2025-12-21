#!/bin/bash
# Safe Git Push Script with Credential Caching

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Git Push Helper ===${NC}\n"

# Check if there are changes
if git diff-index --quiet HEAD -- && git diff --staged --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
    exit 0
fi

# Show changes
echo -e "${YELLOW}Changes to commit:${NC}"
git status --short
echo ""

# Ask for commit message
read -p "Enter commit message: " commit_msg

if [ -z "$commit_msg" ]; then
    commit_msg="Update $(date +%Y-%m-%d)"
fi

# Stage all changes
echo -e "\n${GREEN}Staging changes...${NC}"
git add .

# Commit
echo -e "${GREEN}Creating commit...${NC}"
git commit -m "$commit_msg"

# Configure credential helper (caches credentials for 1 hour)
git config --global credential.helper 'cache --timeout=3600'

# Push
echo -e "\n${GREEN}Pushing to GitHub...${NC}"
echo -e "${YELLOW}Username: md20210${NC}"
echo -e "${YELLOW}Password: <Your GitHub Token>${NC}\n"

if git push; then
    echo -e "\n${GREEN}✅ Successfully pushed to GitHub!${NC}"
    echo -e "${YELLOW}Token is cached for 1 hour - no need to re-enter${NC}"
else
    echo -e "\n${RED}❌ Push failed${NC}"
    exit 1
fi
