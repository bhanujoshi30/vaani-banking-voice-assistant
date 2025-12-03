#!/bin/bash
# Script to generate iOS app icons from the Vaani AI Assistant SVG logo
# This creates all required sizes for iOS app icons

echo "🎨 Generating Vaani Banking iOS App Icons..."
echo ""

# Check if we're in the ios-app directory
if [ ! -f "app-icon-1024.svg" ]; then
    echo "❌ Error: app-icon-1024.svg not found"
    echo "Please run this script from the ios-app directory"
    exit 1
fi

# Create output directory
ICON_DIR="VaaniBankingApp/VaaniBankingApp/Assets.xcassets/AppIcon.appiconset"
mkdir -p "$ICON_DIR"

# Check if ImageMagick or rsvg-convert is available
if command -v rsvg-convert &> /dev/null; then
    CONVERTER="rsvg-convert"
    echo "✅ Using rsvg-convert for SVG to PNG conversion"
elif command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
    echo "✅ Using ImageMagick for SVG to PNG conversion"
else
    echo "❌ Error: Neither rsvg-convert nor ImageMagick found"
    echo ""
    echo "Please install one of these tools:"
    echo "  - rsvg-convert: brew install librsvg"
    echo "  - ImageMagick: brew install imagemagick"
    echo ""
    echo "Alternatively, you can:"
    echo "1. Open app-icon-1024.svg in a browser"
    echo "2. Take a screenshot or export as PNG at 1024x1024"
    echo "3. Use an online tool like https://appicon.co to generate all sizes"
    echo "4. Drag the generated .appiconset folder into Xcode Assets"
    exit 1
fi

echo ""
echo "📐 Generating icon sizes..."

# Function to convert SVG to PNG
convert_svg() {
    local size=$1
    local output=$2
    
    if [ "$CONVERTER" = "rsvg-convert" ]; then
        rsvg-convert -w $size -h $size app-icon-1024.svg -o "$output"
    else
        convert -background none -resize ${size}x${size} app-icon-1024.svg "$output"
    fi
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Generated ${size}x${size} -> $(basename $output)"
    else
        echo "  ✗ Failed to generate ${size}x${size}"
    fi
}

# Generate all required iOS app icon sizes
convert_svg 1024 "$ICON_DIR/icon-1024.png"
convert_svg 180 "$ICON_DIR/icon-60@3x.png"     # iPhone App 60pt @3x
convert_svg 120 "$ICON_DIR/icon-60@2x.png"     # iPhone App 60pt @2x
convert_svg 167 "$ICON_DIR/icon-83.5@2x.png"   # iPad Pro App 83.5pt @2x
convert_svg 152 "$ICON_DIR/icon-76@2x.png"     # iPad App 76pt @2x
convert_svg 76 "$ICON_DIR/icon-76.png"         # iPad App 76pt
convert_svg 87 "$ICON_DIR/icon-29@3x.png"      # Settings 29pt @3x
convert_svg 58 "$ICON_DIR/icon-29@2x.png"      # Settings 29pt @2x
convert_svg 29 "$ICON_DIR/icon-29.png"         # Settings 29pt
convert_svg 80 "$ICON_DIR/icon-40@2x.png"      # Spotlight 40pt @2x
convert_svg 120 "$ICON_DIR/icon-40@3x.png"     # Spotlight 40pt @3x
convert_svg 40 "$ICON_DIR/icon-40.png"         # Spotlight 40pt

echo ""
echo "📝 Creating Contents.json..."

# Create Contents.json for Xcode
cat > "$ICON_DIR/Contents.json" << 'EOF'
{
  "images" : [
    {
      "filename" : "icon-40.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "40x40"
    },
    {
      "filename" : "icon-40@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "40x40"
    },
    {
      "filename" : "icon-60@2x.png",
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "60x60"
    },
    {
      "filename" : "icon-60@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "60x60"
    },
    {
      "filename" : "icon-76.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "76x76"
    },
    {
      "filename" : "icon-76@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "76x76"
    },
    {
      "filename" : "icon-83.5@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "83.5x83.5"
    },
    {
      "filename" : "icon-1024.png",
      "idiom" : "ios-marketing",
      "scale" : "1x",
      "size" : "1024x1024"
    },
    {
      "filename" : "icon-29.png",
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "29x29"
    },
    {
      "filename" : "icon-29@2x.png",
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "29x29"
    },
    {
      "filename" : "icon-29@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "29x29"
    },
    {
      "filename" : "icon-40@3x.png",
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "40x40"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

echo "  ✓ Created Contents.json"
echo ""
echo "✅ App icons generated successfully!"
echo ""
echo "📱 Next steps in Xcode:"
echo "  1. Open VaaniBankingApp.xcodeproj"
echo "  2. Select Assets.xcassets in the project navigator"
echo "  3. Select AppIcon"
echo "  4. The icons should already be there!"
echo "  5. Build and run to see your new app icon"
echo ""
echo "🎉 Done!"
