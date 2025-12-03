#!/usr/bin/env python3
"""
Generate iOS app icons from SVG using cairosvg or online conversion
Falls back to instructions if dependencies aren't available
"""

import os
import sys
from pathlib import Path

def check_cairosvg():
    """Check if cairosvg is available"""
    try:
        import cairosvg
        return True
    except ImportError:
        return False

def generate_icons_with_cairosvg():
    """Generate all iOS app icon sizes using cairosvg"""
    import cairosvg
    
    svg_file = "app-icon-1024.svg"
    icon_dir = Path("VaaniBankingApp/VaaniBankingApp/Assets.xcassets/AppIcon.appiconset")
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    # Icon sizes needed for iOS
    sizes = {
        "icon-1024.png": 1024,
        "icon-60@3x.png": 180,
        "icon-60@2x.png": 120,
        "icon-83.5@2x.png": 167,
        "icon-76@2x.png": 152,
        "icon-76.png": 76,
        "icon-29@3x.png": 87,
        "icon-29@2x.png": 58,
        "icon-29.png": 29,
        "icon-40@2x.png": 80,
        "icon-40@3x.png": 120,
        "icon-40.png": 40,
    }
    
    print("🎨 Generating Vaani Banking iOS App Icons...")
    print(f"📐 Generating {len(sizes)} icon sizes...\n")
    
    for filename, size in sizes.items():
        output_path = icon_dir / filename
        try:
            cairosvg.svg2png(
                url=svg_file,
                write_to=str(output_path),
                output_width=size,
                output_height=size
            )
            print(f"  ✓ Generated {size}x{size} -> {filename}")
        except Exception as e:
            print(f"  ✗ Failed to generate {filename}: {e}")
    
    # Create Contents.json
    contents_json = """{
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
}"""
    
    contents_path = icon_dir / "Contents.json"
    contents_path.write_text(contents_json)
    print("\n  ✓ Created Contents.json")
    
    print("\n✅ App icons generated successfully!")
    print("\n📱 Next steps in Xcode:")
    print("  1. Open VaaniBankingApp.xcodeproj")
    print("  2. Select Assets.xcassets in the project navigator")
    print("  3. Select AppIcon")
    print("  4. The icons should already be there!")
    print("  5. Build and run to see your new app icon")
    print("\n🎉 Done!")

def main():
    print("🍎 Vaani Banking iOS App Icon Generator\n")
    
    # Check if SVG file exists
    if not os.path.exists("app-icon-1024.svg"):
        print("❌ Error: app-icon-1024.svg not found")
        print("Please run this script from the ios-app directory")
        return 1
    
    # Try cairosvg first
    if check_cairosvg():
        print("✅ Using cairosvg for SVG to PNG conversion\n")
        generate_icons_with_cairosvg()
        return 0
    
    # If cairosvg not available, provide instructions
    print("⚠️  cairosvg not installed\n")
    print("📦 Quick install:")
    print("   pip3 install cairosvg")
    print("\n🔄 Alternative methods:")
    print("   1. Install librsvg: brew install librsvg")
    print("      Then run: ./generate-app-icons.sh")
    print("\n   2. Use online tool: https://appicon.co")
    print("      - Open app-icon-1024.svg in browser")
    print("      - Export as 1024x1024 PNG")
    print("      - Upload to appicon.co")
    print("      - Download and use in Xcode")
    print("\n   3. Install cairosvg and re-run:")
    print("      pip3 install cairosvg")
    print("      python3 generate-app-icons.py")
    print("\n📖 See APP_ICON_SETUP.md for detailed instructions")
    return 1

if __name__ == "__main__":
    sys.exit(main())
