#!/bin/bash
# Setup script to configure Xcode command line tools and test deep linking

echo "🔧 Setting up Xcode Command Line Tools..."
echo ""
echo "This will switch your Xcode command line tools to use Xcode.app"
echo "You'll need to enter your password."
echo ""

sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

if [ $? -eq 0 ]; then
    echo "✅ Xcode command line tools configured successfully!"
    echo ""
    
    # Verify simctl is now available
    echo "🔍 Verifying simctl is available..."
    if command -v xcrun simctl &> /dev/null; then
        echo "✅ simctl is now available!"
        echo ""
        
        # List available simulators
        echo "📱 Available iOS Simulators:"
        xcrun simctl list devices available | grep "iPhone"
        echo ""
        
        # Check if any simulator is booted
        BOOTED=$(xcrun simctl list devices | grep "Booted" | head -n 1)
        
        if [ -z "$BOOTED" ]; then
            echo "⚠️  No simulator is currently running."
            echo ""
            echo "To test deep linking:"
            echo "1. Open Xcode and run your VaaniBankingApp on a simulator"
            echo "2. Once the app is running, execute this command:"
            echo ""
            echo "   xcrun simctl openurl booted \"vaani://chat?message=Check%20balance\""
            echo ""
        else
            echo "✅ Simulator is running!"
            echo ""
            echo "🧪 Testing deep link..."
            echo "Opening: vaani://chat?message=Check%20balance"
            xcrun simctl openurl booted "vaani://chat?message=Check%20balance"
            
            if [ $? -eq 0 ]; then
                echo "✅ Deep link sent successfully!"
                echo ""
                echo "You can also test these commands:"
                echo "  xcrun simctl openurl booted \"vaani://chat?message=Show%20my%20recent%20transactions\""
                echo "  xcrun simctl openurl booted \"vaani://chat?message=Transfer%20money\""
            else
                echo "❌ Failed to send deep link. Make sure your app is running on the simulator."
            fi
        fi
    else
        echo "❌ simctl still not available. Please check Xcode installation."
    fi
else
    echo "❌ Failed to configure Xcode command line tools."
    echo "Please make sure you have admin privileges."
fi
