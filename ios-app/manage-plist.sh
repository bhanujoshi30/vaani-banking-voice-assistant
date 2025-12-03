#!/bin/bash

# Info.plist Sync Script
# This script helps manage the Info.plist files for the Vaani Banking iOS app

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
PROJECT_ROOT="/Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp"
MASTER_PLIST="$PROJECT_ROOT/Info.plist"
RESOURCES_PLIST="$PROJECT_ROOT/VaaniBankingApp/Resources/Info.plist"
BACKUP_PLIST="$PROJECT_ROOT/VaaniBankingApp/Resources/Info.plist.backup"

# Functions
show_help() {
    echo -e "${BLUE}Info.plist Manager for Vaani Banking iOS App${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  sync        Copy master Info.plist to Resources (default)"
    echo "  restore     Restore from backup"
    echo "  backup      Create a new backup"
    echo "  diff        Show differences between master and Resources"
    echo "  edit        Open master Info.plist in default editor"
    echo "  validate    Check if Info.plist is valid XML"
    echo "  help        Show this help message"
    echo ""
}

sync_plist() {
    echo -e "${BLUE}Syncing Info.plist...${NC}"
    
    if [ ! -f "$MASTER_PLIST" ]; then
        echo -e "${YELLOW}Error: Master Info.plist not found at $MASTER_PLIST${NC}"
        exit 1
    fi
    
    cp "$MASTER_PLIST" "$RESOURCES_PLIST"
    echo -e "${GREEN}✓ Copied master Info.plist to Resources${NC}"
    echo -e "  From: $MASTER_PLIST"
    echo -e "  To:   $RESOURCES_PLIST"
}

restore_plist() {
    echo -e "${BLUE}Restoring Info.plist from backup...${NC}"
    
    if [ ! -f "$BACKUP_PLIST" ]; then
        echo -e "${YELLOW}Error: Backup not found at $BACKUP_PLIST${NC}"
        exit 1
    fi
    
    cp "$BACKUP_PLIST" "$RESOURCES_PLIST"
    echo -e "${GREEN}✓ Restored Info.plist from backup${NC}"
}

backup_plist() {
    echo -e "${BLUE}Creating backup...${NC}"
    
    if [ ! -f "$RESOURCES_PLIST" ]; then
        echo -e "${YELLOW}Error: Resources Info.plist not found${NC}"
        exit 1
    fi
    
    cp "$RESOURCES_PLIST" "$BACKUP_PLIST"
    echo -e "${GREEN}✓ Backup created at $BACKUP_PLIST${NC}"
}

diff_plist() {
    echo -e "${BLUE}Comparing Info.plist files...${NC}"
    echo ""
    
    if [ ! -f "$MASTER_PLIST" ] || [ ! -f "$RESOURCES_PLIST" ]; then
        echo -e "${YELLOW}Error: One or both files not found${NC}"
        exit 1
    fi
    
    if diff -u "$RESOURCES_PLIST" "$MASTER_PLIST"; then
        echo -e "${GREEN}✓ Files are identical${NC}"
    else
        echo -e "${YELLOW}Files differ (see above)${NC}"
    fi
}

edit_plist() {
    echo -e "${BLUE}Opening master Info.plist...${NC}"
    
    if [ ! -f "$MASTER_PLIST" ]; then
        echo -e "${YELLOW}Error: Master Info.plist not found${NC}"
        exit 1
    fi
    
    open -a Xcode "$MASTER_PLIST" 2>/dev/null || \
    open -e "$MASTER_PLIST" 2>/dev/null || \
    nano "$MASTER_PLIST"
}

validate_plist() {
    echo -e "${BLUE}Validating Info.plist files...${NC}"
    echo ""
    
    if [ -f "$MASTER_PLIST" ]; then
        echo -n "Master Info.plist: "
        if plutil -lint "$MASTER_PLIST" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Valid${NC}"
        else
            echo -e "${YELLOW}✗ Invalid XML${NC}"
            plutil -lint "$MASTER_PLIST"
        fi
    fi
    
    if [ -f "$RESOURCES_PLIST" ]; then
        echo -n "Resources Info.plist: "
        if plutil -lint "$RESOURCES_PLIST" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Valid${NC}"
        else
            echo -e "${YELLOW}✗ Invalid XML${NC}"
            plutil -lint "$RESOURCES_PLIST"
        fi
    fi
}

# Main script
case "${1:-sync}" in
    sync)
        sync_plist
        ;;
    restore)
        restore_plist
        ;;
    backup)
        backup_plist
        ;;
    diff)
        diff_plist
        ;;
    edit)
        edit_plist
        ;;
    validate)
        validate_plist
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${YELLOW}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
