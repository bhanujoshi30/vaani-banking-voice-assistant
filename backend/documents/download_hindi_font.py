#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download Noto Sans Devanagari font for Hindi PDF generation
"""
import urllib.request
import ssl
import os
from pathlib import Path

# Create SSL context that doesn't verify certificates (for corporate networks)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def download_noto_font():
    """Download Noto Sans Devanagari font"""
    font_dir = Path(__file__).parent / "fonts"
    font_dir.mkdir(exist_ok=True)
    
    # Updated URLs - using GitHub API or direct CDN links
    font_urls = {
        'regular': 'https://github.com/google/fonts/raw/main/apache/notosansdevanagari/NotoSansDevanagari-Regular.ttf',
        'bold': 'https://github.com/google/fonts/raw/main/apache/notosansdevanagari/NotoSansDevanagari-Bold.ttf',
    }
    
    # Alternative: Use Google Fonts CDN (if GitHub fails)
    alt_urls = {
        'regular': 'https://fonts.gstatic.com/s/notosansdevanagari/v33/TuGoUUFzXI5FBtUq5a8bnKIOdTwQNO_W3fJJJcI.ttf',
        'bold': 'https://fonts.gstatic.com/s/notosansdevanagari/v33/TuGpUUFzXI5FBtUq5a8bnKIOdTwQNO_W3fJJJcI.ttf',
    }
    
    downloaded = []
    
    for variant, url in font_urls.items():
        variant_capitalized = variant.capitalize()
        font_filename = "NotoSansDevanagari-{}.ttf".format(variant_capitalized)
        font_path = font_dir / font_filename
        
        if font_path.exists():
            print("✅ Font already exists: {}".format(font_path))
            downloaded.append(str(font_path))
            continue
        
        # Try primary URL first
        success = False
        try:
            print("📥 Downloading {} font from GitHub...".format(variant))
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ssl_context) as response:
                with open(str(font_path), 'wb') as out_file:
                    out_file.write(response.read())
            print("✅ Downloaded: {}".format(font_path))
            downloaded.append(str(font_path))
            success = True
        except Exception as e:
            print("⚠️  GitHub download failed: {}".format(e))
            # Try alternative CDN URL
            try:
                alt_url = alt_urls[variant]
                print("📥 Trying alternative CDN URL...")
                req = urllib.request.Request(alt_url)
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    with open(str(font_path), 'wb') as out_file:
                        out_file.write(response.read())
                print("✅ Downloaded from CDN: {}".format(font_path))
                downloaded.append(str(font_path))
                success = True
            except Exception as e2:
                print("❌ CDN download also failed: {}".format(e2))
        
        if not success:
            print("   Please download manually from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
            print("   Save as: {}".format(font_path))
    
    return downloaded

if __name__ == "__main__":
    print("=" * 60)
    print("Downloading Noto Sans Devanagari Font")
    print("=" * 60)
    fonts = download_noto_font()
    if fonts:
        print("\n✅ Fonts ready at: {}".format(fonts[0]))
        print("   You can now regenerate Hindi PDFs with proper fonts!")
    else:
        print("\n❌ Font download failed. Please download manually.")
