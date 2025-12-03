#!/bin/bash

# AppState Error Fix - Validation and Cleanup Script
# Run this script to verify the fix and clean Xcode caches

set -e

echo "🔍 Validating AppState Fix..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/ashok/Documents/projects/vaani-deploment-trails/vaani-banking-voice-assistant/ios-app/VaaniBankingApp"

# Check if AppState.swift exists
echo -e "${BLUE}1. Checking AppState.swift file...${NC}"
if [ -f "$PROJECT_DIR/VaaniBankingApp/Bridge/AppState.swift" ]; then
    echo -e "${GREEN}✓ AppState.swift found${NC}"
    echo "  Location: VaaniBankingApp/Bridge/AppState.swift"
else
    echo -e "${RED}✗ AppState.swift NOT found${NC}"
    exit 1
fi

# Verify AppState conforms to ObservableObject
echo ""
echo -e "${BLUE}2. Verifying ObservableObject conformance...${NC}"
if grep -q "class AppState: ObservableObject" "$PROJECT_DIR/VaaniBankingApp/Bridge/AppState.swift"; then
    echo -e "${GREEN}✓ AppState conforms to ObservableObject${NC}"
else
    echo -e "${RED}✗ AppState does not conform to ObservableObject${NC}"
    exit 1
fi

# Verify @Published property exists
echo ""
echo -e "${BLUE}3. Verifying @Published property...${NC}"
if grep -q "@Published var pendingMessage" "$PROJECT_DIR/VaaniBankingApp/Bridge/AppState.swift"; then
    echo -e "${GREEN}✓ @Published pendingMessage property found${NC}"
else
    echo -e "${YELLOW}⚠ @Published property not found (may cause issues)${NC}"
fi

# Check VaaniBankingApp.swift for duplicate
echo ""
echo -e "${BLUE}4. Checking for duplicate AppState definition...${NC}"
if grep -q "class AppState: ObservableObject" "$PROJECT_DIR/VaaniBankingApp/VaaniBankingApp.swift"; then
    echo -e "${YELLOW}⚠ WARNING: Duplicate AppState found in VaaniBankingApp.swift${NC}"
    echo "  This should be removed to avoid conflicts"
else
    echo -e "${GREEN}✓ No duplicate AppState definition${NC}"
fi

# Clean derived data
echo ""
echo -e "${BLUE}5. Cleaning Xcode derived data...${NC}"
if [ -d ~/Library/Developer/Xcode/DerivedData ]; then
    echo "  Finding VaaniBankingApp derived data..."
    DERIVED_DATA=$(find ~/Library/Developer/Xcode/DerivedData -name "VaaniBankingApp-*" -type d 2>/dev/null | head -1)
    
    if [ -n "$DERIVED_DATA" ]; then
        echo "  Removing: $DERIVED_DATA"
        rm -rf "$DERIVED_DATA"
        echo -e "${GREEN}✓ Derived data cleaned${NC}"
    else
        echo -e "${YELLOW}  No derived data found (this is OK)${NC}"
    fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ VALIDATION COMPLETE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps in Xcode:"
echo "1. Open VaaniBankingApp.xcodeproj"
echo "2. Check if AppState.swift is in the Navigator"
echo "3. If not, add it:"
echo "   - Right-click 'Bridge' folder"
echo "   - 'Add Files to VaaniBankingApp...'"
echo "   - Select Bridge/AppState.swift"
echo "   - Uncheck 'Copy items if needed'"
echo "   - Check 'VaaniBankingApp' target"
echo "4. Clean Build Folder (⇧⌘K)"
echo "5. Build (⌘B)"
echo ""
echo -e "${BLUE}If error persists:${NC}"
echo "• Restart Xcode"
echo "• Run: rm -rf ~/Library/Developer/Xcode/DerivedData"
echo "• Clean and rebuild"
echo ""
