#!/bin/bash
#
# Migration Script: Transfer GoalieScout-BDC-2026 to New Repository
#
# This script automates the process of transferring the BDC 2026 work
# from the GoalieScout repository to the new GoalieScout-BDC-2026 repository.
#
# Usage: ./migrate_to_new_repo.sh [NEW_REPO_URL]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BRANCH_NAME="copilot/adapt-project-for-bdc-2026"
DEFAULT_NEW_REPO="https://github.com/UtahNetScout/GoalieScout-BDC-2026.git"
NEW_REPO="${1:-$DEFAULT_NEW_REPO}"
NEW_REMOTE_NAME="bdc2026"

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  GoalieScout-BDC-2026 Repository Migration Script${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Check current repository
echo -e "${BLUE}[1/7] Checking current repository...${NC}"
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from the GoalieScout repository root."
    exit 1
fi
print_success "Git repository detected"

# Step 2: Check if the branch exists
echo -e "${BLUE}[2/7] Verifying branch existence...${NC}"
if ! git rev-parse --verify "$BRANCH_NAME" > /dev/null 2>&1; then
    print_error "Branch '$BRANCH_NAME' not found. Please ensure you have the correct branch."
    exit 1
fi
print_success "Branch '$BRANCH_NAME' found"

# Step 3: Fetch latest changes
echo -e "${BLUE}[3/7] Fetching latest changes...${NC}"
git fetch origin
print_success "Latest changes fetched"

# Step 4: Checkout the BDC 2026 branch
echo -e "${BLUE}[4/7] Checking out BDC 2026 branch...${NC}"
git checkout "$BRANCH_NAME"
print_success "Checked out branch '$BRANCH_NAME'"

# Step 5: Add new repository as remote
echo -e "${BLUE}[5/7] Adding new repository as remote...${NC}"
print_info "New repository URL: $NEW_REPO"

# Remove remote if it already exists
if git remote | grep -q "^${NEW_REMOTE_NAME}$"; then
    print_info "Remote '$NEW_REMOTE_NAME' already exists, removing..."
    git remote remove "$NEW_REMOTE_NAME"
fi

git remote add "$NEW_REMOTE_NAME" "$NEW_REPO"
print_success "Added remote '$NEW_REMOTE_NAME'"

# Step 6: Verify files to be transferred
echo -e "${BLUE}[6/7] Verifying files to be transferred...${NC}"
FILE_COUNT=$(git ls-files | wc -l)
print_info "Found $FILE_COUNT files to transfer"

# List key files
echo ""
echo "Key files that will be transferred:"
for file in "README.md" "README_BDC_2026.md" "player_movement_scout.py" "requirements.txt" "test_system.py"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (missing!)"
    fi
done
echo ""

# Step 7: Push to new repository
echo -e "${BLUE}[7/7] Pushing to new repository...${NC}"
echo ""
echo -e "${YELLOW}This will push the current branch to the new repository.${NC}"
echo -e "${YELLOW}Choose the target branch:${NC}"
echo "  1) Push to 'main' branch (recommended for new repo)"
echo "  2) Push to '$BRANCH_NAME' branch (preserve branch name)"
echo "  3) Cancel"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        print_info "Pushing to 'main' branch..."
        if git push "$NEW_REMOTE_NAME" "$BRANCH_NAME:main"; then
            print_success "Successfully pushed to main branch!"
        else
            print_error "Push failed. Check your credentials and repository access."
            exit 1
        fi
        ;;
    2)
        print_info "Pushing to '$BRANCH_NAME' branch..."
        if git push "$NEW_REMOTE_NAME" "$BRANCH_NAME:$BRANCH_NAME"; then
            print_success "Successfully pushed to $BRANCH_NAME branch!"
        else
            print_error "Push failed. Check your credentials and repository access."
            exit 1
        fi
        ;;
    3)
        print_info "Migration cancelled by user"
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Migration Complete! 🎉${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Verify the new repository: $NEW_REPO"
echo "  2. Clone and test: git clone $NEW_REPO"
echo "  3. Run tests: python test_system.py"
echo "  4. Update README with new repository URLs"
echo ""
echo "For detailed post-migration steps, see MIGRATION_GUIDE.md"
echo ""
print_success "Migration script completed successfully!"
