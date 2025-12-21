#!/bin/bash
# GitHub SSH Key Setup Script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== GitHub SSH Key Setup ===${NC}\n"

# Check if SSH key already exists
if [ -f ~/.ssh/id_ed25519 ]; then
    echo -e "${YELLOW}SSH key already exists!${NC}"
    echo -e "${BLUE}Your public key:${NC}\n"
    cat ~/.ssh/id_ed25519.pub
    echo -e "\n${YELLOW}Skip to Step 3 below if you already added this to GitHub${NC}\n"
else
    # Generate new SSH key
    echo -e "${GREEN}Step 1: Generating new SSH key...${NC}"
    read -p "Enter your GitHub email (md20210's email): " email

    ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/id_ed25519 -N ""

    echo -e "\n${GREEN}✅ SSH key generated!${NC}\n"
fi

# Start SSH agent
echo -e "${GREEN}Step 2: Starting SSH agent...${NC}"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

echo -e "\n${GREEN}✅ SSH key added to agent!${NC}\n"

# Display public key
echo -e "${GREEN}Step 3: Copy this public key:${NC}\n"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cat ~/.ssh/id_ed25519.pub
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}Step 4: Add to GitHub:${NC}"
echo -e "  1. Open: ${BLUE}https://github.com/settings/ssh/new${NC}"
echo -e "  2. Title: ${GREEN}WSL General Backend${NC}"
echo -e "  3. Paste the key above"
echo -e "  4. Click 'Add SSH key'\n"

read -p "Press Enter when you've added the key to GitHub..."

# Test connection
echo -e "\n${GREEN}Step 5: Testing GitHub connection...${NC}"
ssh -T git@github.com 2>&1 | grep -q "successfully authenticated" && \
    echo -e "${GREEN}✅ SSH connection successful!${NC}" || \
    echo -e "${YELLOW}Note: 'Permission denied' is normal if key not yet added${NC}"

# Update git remote to use SSH
echo -e "\n${GREEN}Step 6: Updating git remote to use SSH...${NC}"
cd /mnt/e/CodeLocalLLM/GeneralBackend
git remote set-url origin git@github.com:md20210/general-backend.git

echo -e "${GREEN}✅ Git remote updated to SSH!${NC}\n"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo -e "${YELLOW}You can now use git push without passwords!${NC}"
echo -e "${BLUE}Test it: git push${NC}\n"
