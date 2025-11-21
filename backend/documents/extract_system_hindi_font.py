#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Hindi fonts from system TrueType Collections (.ttc files)
This is useful when fonts are already installed on the system
"""
import os
import sys
from pathlib import Path

def extract_system_fonts():
    """Extract Hindi fonts from system .ttc files"""
    fonts_dir = Path(__file__).parent / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    try:
        from fontTools.ttLib import TTFont as FontToolsTTFont
    except ImportError:
        print("❌ ERROR: fonttools is not installed")
        print("   Install with: pip install fonttools")
        return False
    
    # macOS system font paths
    system_fonts = [
        '/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc',
        '/System/Library/Fonts/Supplemental/ITFDevanagari.ttc',
        '/System/Library/Fonts/Supplemental/DevanagariMT.ttc',
    ]
    
    extracted = []
    
    for ttc_path in system_fonts:
        if not os.path.exists(ttc_path):
            continue
        
        try:
            print("📖 Reading font collection: {}".format(os.path.basename(ttc_path)))
            
            # Open the TTC file
            ttc = FontToolsTTFont(ttc_path, fontNumber=0)
            
            # Extract font name from the font itself
            font_name = "NotoSansDevanagari"
            if 'name' in ttc:
                for name_record in ttc['name'].names:
                    if name_record.nameID == 4:  # Full font name
                        font_name = name_record.toUnicode().replace(' ', '')
                        break
            
            # Save as .ttf
            regular_path = fonts_dir / "{}Regular.ttf".format(font_name)
            ttc.save(str(regular_path))
            print("✅ Extracted: {}".format(regular_path))
            extracted.append(str(regular_path))
            
            # Try to get bold variant (fontNumber=1 or search)
            try:
                ttc_bold = FontToolsTTFont(ttc_path, fontNumber=1)
                bold_path = fonts_dir / "{}Bold.ttf".format(font_name)
                ttc_bold.save(str(bold_path))
                print("✅ Extracted bold: {}".format(bold_path))
                extracted.append(str(bold_path))
            except:
                # If no bold variant, use regular for both
                bold_path = fonts_dir / "{}Bold.ttf".format(font_name)
                ttc.save(str(bold_path))
                print("✅ Created bold alias: {}".format(bold_path))
                extracted.append(str(bold_path))
            
            # Use the first successful extraction
            break
            
        except Exception as e:
            print("⚠️  Failed to extract from {}: {}".format(ttc_path, e))
            continue
    
    if extracted:
        print("\n✅ Successfully extracted fonts:")
        for font_path in extracted:
            print("   - {}".format(font_path))
        print("\n💡 Tip: Rename to NotoSansDevanagari-Regular.ttf and NotoSansDevanagari-Bold.ttf")
        print("   if you want to use the standard naming convention.")
        return True
    else:
        print("\n❌ No fonts could be extracted.")
        print("   Please download fonts manually or install fonttools and try again.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Extract Hindi Fonts from System")
    print("=" * 60)
    extract_system_fonts()

