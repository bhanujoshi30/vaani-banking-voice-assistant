#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Hindi font rendering in ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from pathlib import Path
import os

def find_hindi_fonts():
    """Find available Hindi/Devanagari fonts on the system"""
    font_paths = []
    
    # macOS paths
    mac_paths = [
        '/System/Library/Fonts/Supplemental/',
        '/Library/Fonts/',
        os.path.expanduser('~/Library/Fonts/'),
    ]
    
    # Linux paths
    linux_paths = [
        '/usr/share/fonts/truetype/noto/',
        '/usr/share/fonts/truetype/dejavu/',
    ]
    
    # Windows paths
    windows_paths = [
        'C:/Windows/Fonts/',
    ]
    
    all_paths = mac_paths + linux_paths + windows_paths
    
    for base_path in all_paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if any(keyword in file.lower() for keyword in ['devanagari', 'hindi', 'noto', 'mangal']):
                        full_path = os.path.join(root, file)
                        font_paths.append(full_path)
    
    return font_paths

def register_hindi_font():
    """Try to register a Hindi-supporting font"""
    font_paths = find_hindi_fonts()
    
    print("Found Hindi font candidates:")
    for path in font_paths[:10]:  # Show first 10
        print(f"  - {path}")
    
    # Try to register fonts (prefer .ttf, but also try .ttc)
    for font_path in font_paths:
        try:
            if font_path.endswith('.ttf'):
                pdfmetrics.registerFont(TTFont('HindiFont', font_path))
                print(f"\n✅ Successfully registered: {font_path} as 'HindiFont'")
                
                # Try to register bold variant
                bold_path = font_path.replace('Regular', 'Bold').replace('regular', 'bold')
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont('HindiFontBold', bold_path))
                    print(f"✅ Successfully registered bold: {bold_path} as 'HindiFontBold'")
                    return 'HindiFont', 'HindiFontBold'
                else:
                    # Use same font for bold
                    pdfmetrics.registerFont(TTFont('HindiFontBold', font_path))
                    return 'HindiFont', 'HindiFontBold'
        except Exception as e:
            print(f"⚠️  Failed to register {font_path}: {e}")
            continue
    
    # Fallback: Try system fonts that might work
    print("\n⚠️  No suitable Hindi fonts found. Trying system fonts...")
    try:
        # Try using a Unicode-supporting font that might be available
        # ReportLab's default fonts don't support Hindi, so we need a fallback
        return 'Helvetica', 'Helvetica-Bold'
    except:
        return None, None

def test_hindi_pdf():
    """Create a test PDF with Hindi text"""
    output_path = Path(__file__).parent / "test_hindi_output.pdf"
    
    # Register font
    hindi_font, hindi_font_bold = register_hindi_font()
    
    if not hindi_font:
        print("❌ ERROR: Could not register any Hindi font!")
        return False
    
    print(f"\n📝 Creating test PDF with font: {hindi_font}")
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Create styles with Hindi font
    title_style = ParagraphStyle(
        'HindiTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF8F42'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=hindi_font_bold
    )
    
    normal_style = ParagraphStyle(
        'HindiNormal',
        parent=styles['Normal'],
        fontSize=12,
        fontName=hindi_font
    )
    
    # Test Hindi text
    test_texts = [
        "होम लोन",
        "पर्सनल लोन",
        "ऑटो लोन",
        "सन नेशनल बैंक का होम लोन आपको अपना घर खरीदने के सपने को पूरा करने में मदद करने के लिए बनाया गया है।",
        "ब्याज दर: 8.35% - 9.50% प्रति वर्ष",
        "लोन राशि: Rs. 5 लाख से Rs. 5 करोड़",
    ]
    
    story.append(Paragraph("Hindi Font Test", title_style))
    story.append(Spacer(1, 20))
    
    for text in test_texts:
        story.append(Paragraph(text, normal_style))
        story.append(Spacer(1, 10))
    
    try:
        doc.build(story)
        print(f"✅ Test PDF created successfully: {output_path}")
        print(f"   Please open the PDF and verify Hindi text is readable")
        return True
    except Exception as e:
        print(f"❌ ERROR creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Hindi Font Test Script")
    print("=" * 60)
    test_hindi_pdf()

