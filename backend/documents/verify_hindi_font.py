#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Hindi font registration and test rendering
Run this before generating PDFs to ensure fonts are working
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    import os
    
    print("=" * 60)
    print("Hindi Font Verification Script")
    print("=" * 60)
    
    # Test Hindi text
    test_text = "होम लोन"
    print(f"\n📝 Test Hindi text: {test_text}")
    
    # Try to register font using the same logic as the main script
    fonts_dir = Path(__file__).parent / "fonts"
    noto_regular = fonts_dir / "NotoSansDevanagari-Regular.ttf"
    
    font_registered = False
    
    # Check for downloaded font first
    if noto_regular.exists():
        try:
            pdfmetrics.registerFont(TTFont('TestHindiFont', str(noto_regular)))
            print(f"✅ Registered downloaded font: {noto_regular}")
            font_registered = True
            font_name = 'TestHindiFont'
        except Exception as e:
            print(f"❌ Failed to register downloaded font: {e}")
    
    # Try system fonts
    if not font_registered:
        import platform
        if platform.system() == 'Darwin':
            system_fonts = [
                '/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc',
                '/System/Library/Fonts/Supplemental/ITFDevanagari.ttc',
                '/System/Library/Fonts/Supplemental/DevanagariMT.ttc',
            ]
            
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    try:
                        # Try extracting with fonttools
                        from fontTools.ttLib import TTFont as FontToolsTTFont
                        ttc = FontToolsTTFont(font_path, fontNumber=0)
                        temp_ttf = fonts_dir / f"test_extracted_{os.path.basename(font_path).replace('.ttc', '.ttf')}"
                        fonts_dir.mkdir(exist_ok=True)
                        ttc.save(str(temp_ttf))
                        pdfmetrics.registerFont(TTFont('TestHindiFont', str(temp_ttf)))
                        print(f"✅ Extracted and registered system font: {font_path}")
                        font_registered = True
                        font_name = 'TestHindiFont'
                        break
                    except ImportError:
                        print("⚠️  fonttools not installed. Install with: pip install fonttools")
                        break
                    except Exception as e:
                        print(f"⚠️  Failed to extract {font_path}: {e}")
                        continue
    
    if not font_registered:
        print("\n❌ ERROR: Could not register any Hindi font!")
        print("\nTo fix this:")
        print("1. Download Hindi font:")
        print("   python download_hindi_font.py")
        print("2. Or install fonttools and system fonts will be extracted:")
        print("   pip install fonttools")
        sys.exit(1)
    
    # Create test PDF
    print(f"\n🔄 Creating test PDF with font: {font_name}")
    output_path = Path(__file__).parent / "test_hindi_verification.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TestTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF8F42'),
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    normal_style = ParagraphStyle(
        'TestNormal',
        parent=styles['Normal'],
        fontSize=14,
        fontName=font_name
    )
    
    # Test various Hindi texts
    test_texts = [
        "होम लोन",
        "पर्सनल लोन",
        "ऑटो लोन",
        "ब्याज दर: 8.35% - 9.50% प्रति वर्ष",
        "लोन राशि: Rs. 5 लाख से Rs. 5 करोड़",
        "सन नेशनल बैंक का होम लोन आपको अपना घर खरीदने के सपने को पूरा करने में मदद करने के लिए बनाया गया है।",
    ]
    
    story.append(Paragraph("Hindi Font Test", title_style))
    story.append(Paragraph("", normal_style))
    
    for text in test_texts:
        story.append(Paragraph(text, normal_style))
        story.append(Paragraph("", normal_style))
    
    try:
        doc.build(story)
        print(f"✅ Test PDF created: {output_path}")
        print(f"\n📖 Please open the PDF and verify:")
        print(f"   1. Hindi text is readable (not colored blocks)")
        print(f"   2. All characters render correctly")
        print(f"   3. Font looks good")
        print(f"\nIf the PDF looks good, you can regenerate Hindi documents!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR creating test PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

except ImportError as e:
    print(f"❌ ERROR: Missing required library: {e}")
    print("   Install with: pip install reportlab")
    if 'fonttools' in str(e):
        print("   Also install: pip install fonttools")
    sys.exit(1)

