#!/bin/bash
# Quick commands for iOS app development and testing

echo "🍎 Vaani Banking iOS App - Quick Commands"
echo "=========================================="
echo ""

# Check if simctl is available
if ! command -v xcrun simctl &> /dev/null; then
    echo "⚠️  simctl not available. Run: ./setup-simctl.sh"
    echo ""
    exit 1
fi

PS3='Select an option: '
options=(
    "List available simulators"
    "Boot iPhone 15 Pro simulator"
    "Test: Check Balance deep link"
    "Test: View Transactions deep link"
    "Test: Transfer Money deep link"
    "Test: Custom message deep link"
    "Show running simulators"
    "Open Shortcuts app on simulator"
    "Build app (command line)"
    "Clean build folder"
    "Show device logs"
    "Quit"
)

select opt in "${options[@]}"
do
    case $opt in
        "List available simulators")
            echo ""
            echo "📱 Available iOS Simulators:"
            xcrun simctl list devices available | grep "iPhone"
            echo ""
            ;;
        "Boot iPhone 15 Pro simulator")
            echo ""
            echo "🚀 Booting iPhone 15 Pro..."
            xcrun simctl boot "iPhone 15 Pro" 2>/dev/null && echo "✅ Booted!" || echo "Already running or device not found"
            echo ""
            ;;
        "Test: Check Balance deep link")
            echo ""
            echo "🧪 Testing: vaani://chat?message=Check%20balance"
            xcrun simctl openurl booted "vaani://chat?message=Check%20balance"
            echo "✅ Deep link sent!"
            echo ""
            ;;
        "Test: View Transactions deep link")
            echo ""
            echo "🧪 Testing: vaani://chat?message=Show%20my%20recent%20transactions"
            xcrun simctl openurl booted "vaani://chat?message=Show%20my%20recent%20transactions"
            echo "✅ Deep link sent!"
            echo ""
            ;;
        "Test: Transfer Money deep link")
            echo ""
            echo "🧪 Testing: vaani://chat?message=Transfer%20money"
            xcrun simctl openurl booted "vaani://chat?message=Transfer%20money"
            echo "✅ Deep link sent!"
            echo ""
            ;;
        "Test: Custom message deep link")
            echo ""
            read -p "Enter message (spaces allowed): " custom_msg
            encoded_msg=$(echo "$custom_msg" | jq -sRr @uri)
            echo "🧪 Testing: vaani://chat?message=$encoded_msg"
            xcrun simctl openurl booted "vaani://chat?message=$encoded_msg"
            echo "✅ Deep link sent!"
            echo ""
            ;;
        "Show running simulators")
            echo ""
            echo "🏃 Currently running simulators:"
            xcrun simctl list devices | grep "Booted"
            echo ""
            ;;
        "Open Shortcuts app on simulator")
            echo ""
            echo "📲 Opening Shortcuts app..."
            xcrun simctl openurl booted "shortcuts://"
            echo "✅ Shortcuts app opened (if installed)"
            echo ""
            ;;
        "Build app (command line)")
            echo ""
            echo "🔨 Building VaaniBankingApp..."
            cd VaaniBankingApp
            xcodebuild -project VaaniBankingApp.xcodeproj -scheme VaaniBankingApp -destination 'platform=iOS Simulator,name=iPhone 15 Pro' build
            echo ""
            ;;
        "Clean build folder")
            echo ""
            echo "🧹 Cleaning build folder..."
            cd VaaniBankingApp
            xcodebuild clean -project VaaniBankingApp.xcodeproj -scheme VaaniBankingApp
            echo "✅ Build folder cleaned!"
            echo ""
            ;;
        "Show device logs")
            echo ""
            echo "📋 Showing simulator logs (Ctrl+C to stop)..."
            xcrun simctl spawn booted log stream --predicate 'processImagePath contains "VaaniBankingApp"'
            echo ""
            ;;
        "Quit")
            echo ""
            echo "👋 Goodbye!"
            break
            ;;
        *) 
            echo "Invalid option $REPLY"
            ;;
    esac
done
