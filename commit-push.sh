#!/bin/bash

# Commit and push script for ArmGPT-server
# Automates git commit and push workflow

echo "🚀 Git Commit & Push Script"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check git status
check_status() {
    echo -e "\n📊 Checking git status..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: Not in a git repository${NC}"
        exit 1
    fi
    
    # Show current branch
    current_branch=$(git branch --show-current)
    echo -e "📍 Current branch: ${GREEN}$current_branch${NC}"
    
    # Check for changes
    if [[ -z $(git status -s) ]]; then
        echo -e "${YELLOW}⚠️  No changes to commit${NC}"
        exit 0
    fi
    
    # Show status
    git status -s
}

# Function to stage changes
stage_changes() {
    echo -e "\n📝 Staging changes..."
    
    # Check if there are any changes to stage
    if [[ -n $(git diff --name-only) ]] || [[ -n $(git ls-files --others --exclude-standard) ]]; then
        echo "The following files will be staged:"
        git diff --name-only
        git ls-files --others --exclude-standard
        
        echo -e "\n${YELLOW}Stage all changes? (y/n):${NC} "
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            git add -A
            echo -e "${GREEN}✅ Changes staged${NC}"
        else
            echo "Selective staging - add files manually with 'git add <file>'"
            exit 0
        fi
    else
        echo "No unstaged changes found"
    fi
}

# Function to commit changes
commit_changes() {
    echo -e "\n💬 Creating commit..."
    
    # Check if there are staged changes
    if [[ -z $(git diff --cached --name-only) ]]; then
        echo -e "${YELLOW}⚠️  No staged changes to commit${NC}"
        exit 0
    fi
    
    # Show what will be committed
    echo "Files to be committed:"
    git diff --cached --name-status
    
    # Get commit message
    echo -e "\n${YELLOW}Enter commit message (or 'q' to quit):${NC} "
    read -r commit_message
    
    if [[ "$commit_message" == "q" ]]; then
        echo "Commit cancelled"
        exit 0
    fi
    
    if [[ -z "$commit_message" ]]; then
        echo -e "${RED}❌ Error: Commit message cannot be empty${NC}"
        exit 1
    fi
    
    # Commit
    git commit -m "$commit_message"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Changes committed successfully${NC}"
    else
        echo -e "${RED}❌ Error: Commit failed${NC}"
        exit 1
    fi
}

# Function to push changes
push_changes() {
    echo -e "\n🔄 Pushing to remote..."
    
    # Get current branch
    current_branch=$(git branch --show-current)
    
    # Check if branch has upstream
    if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  No upstream branch set${NC}"
        echo -e "Push and set upstream? (y/n): "
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            git push -u origin "$current_branch"
        else
            echo "Push cancelled"
            exit 0
        fi
    else
        # Normal push
        git push
    fi
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Changes pushed successfully${NC}"
        
        # Show remote URL
        remote_url=$(git remote get-url origin 2>/dev/null)
        if [[ -n "$remote_url" ]]; then
            echo -e "📍 Remote: $remote_url"
        fi
    else
        echo -e "${RED}❌ Error: Push failed${NC}"
        exit 1
    fi
}

# Function for quick commit and push
quick_mode() {
    echo -e "${YELLOW}Quick mode - committing all changes${NC}"
    
    # Check for changes
    if [[ -z $(git status -s) ]]; then
        echo -e "${YELLOW}⚠️  No changes to commit${NC}"
        exit 0
    fi
    
    # Get commit message
    echo -e "Enter commit message: "
    read -r commit_message
    
    if [[ -z "$commit_message" ]]; then
        echo -e "${RED}❌ Error: Commit message cannot be empty${NC}"
        exit 1
    fi
    
    # Stage, commit, and push
    git add -A
    git commit -m "$commit_message"
    git push
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ All done!${NC}"
    fi
}

# Main execution
main() {
    case "$1" in
        --quick|-q)
            quick_mode
            ;;
        --status|-s)
            check_status
            ;;
        --help|-h)
            echo "Usage: $0 [option]"
            echo "Options:"
            echo "  --quick, -q     Quick mode (stage all, commit, push)"
            echo "  --status, -s    Show git status only"
            echo "  --help, -h      Show this help message"
            echo "  (no option)     Interactive mode"
            ;;
        *)
            # Interactive mode
            check_status
            stage_changes
            commit_changes
            
            echo -e "\n${YELLOW}Push changes to remote? (y/n):${NC} "
            read -r response
            
            if [[ "$response" =~ ^[Yy]$ ]]; then
                push_changes
            else
                echo "Changes committed locally. Use 'git push' when ready."
            fi
            
            echo -e "\n${GREEN}✨ Done!${NC}"
            ;;
    esac
}

# Run main function with all arguments
main "$@"