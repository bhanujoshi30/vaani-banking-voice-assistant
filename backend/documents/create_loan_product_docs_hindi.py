# -*- coding: utf-8 -*-
"""
Create Comprehensive Loan Product Documentation in Hindi for RAG
These PDFs contain detailed information about each loan type offered by Sun National Bank in Hindi
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import re
import os

# Register Hindi-supporting font
def register_hindi_font():
    """Register a Hindi-supporting font for PDF generation"""
    import platform
    
    # FIRST: Check for any Hindi font in fonts directory (extracted fonts)
    fonts_dir = Path(__file__).parent / "fonts"
    if fonts_dir.exists():
        font_files = list(fonts_dir.glob("*.ttf"))
        regular_font = None
        bold_font = None
        
        # Look for regular and bold fonts (prioritize Regular)
        for font_file in font_files:
            font_name_lower = font_file.name.lower()
            if 'regular' in font_name_lower and not regular_font:
                regular_font = font_file
            elif 'bold' in font_name_lower and not bold_font:
                bold_font = font_file
        
        # If no regular found, look for any Devanagari font (but not bold)
        if not regular_font:
            for font_file in font_files:
                font_name_lower = font_file.name.lower()
                if 'devanagari' in font_name_lower and 'bold' not in font_name_lower:
                    regular_font = font_file
                    break
        
        # If still no regular found, use first non-bold font
        if not regular_font and font_files:
            for font_file in font_files:
                if 'bold' not in font_file.name.lower():
                    regular_font = font_file
                    break
            # If all fonts are bold, use first one anyway
            if not regular_font:
                regular_font = font_files[0]
        
        # If no bold found, use regular for both
        if not bold_font:
            bold_font = regular_font
        
        if regular_font:
            try:
                pdfmetrics.registerFont(TTFont('HindiFont', str(regular_font)))
                pdfmetrics.registerFont(TTFont('HindiFontBold', str(bold_font)))
                print("✅ Using Hindi font from fonts directory: {}".format(regular_font.name))
                return 'HindiFont', 'HindiFontBold'
            except Exception as e:
                print("⚠️  Failed to register font from fonts directory: {}".format(e))
    
    # SECOND: Find Hindi/Devanagari fonts on the system
    font_candidates = []
    
    # macOS - check for Devanagari fonts (.ttc files work with ReportLab)
    if platform.system() == 'Darwin':
        mac_font_dirs = [
            '/System/Library/Fonts/Supplemental/',
            '/Library/Fonts/',
            os.path.expanduser('~/Library/Fonts/'),
        ]
        for font_dir in mac_font_dirs:
            if os.path.exists(font_dir):
                for file in os.listdir(font_dir):
                    if any(keyword in file.lower() for keyword in ['devanagari', 'hindi', 'noto']):
                        font_path = os.path.join(font_dir, file)
                        # ReportLab can handle .ttc files, but we need to extract the font
                        if file.endswith('.ttc'):
                            # For .ttc files, we'll try to use them directly
                            # ReportLab should handle TrueType Collections
                            font_candidates.append(('ttc', font_path))
                        elif file.endswith('.ttf'):
                            font_candidates.append(('ttf', font_path))
    
    # Linux paths
    linux_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in linux_paths:
        if os.path.exists(path):
            font_candidates.append(('ttf', path))
    
    # Windows paths
    windows_paths = [
        'C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf',
        'C:/Windows/Fonts/mangal.ttf',
    ]
    for path in windows_paths:
        if os.path.exists(path):
            font_candidates.append(('ttf', path))
    
    # Try to register fonts
    for font_type, font_path in font_candidates:
        try:
            if font_type == 'ttc':
                # For .ttc files, try extracting using fonttools
                try:
                    from fontTools.ttLib import TTFont as FontToolsTTFont
                    # Extract first font from collection
                    ttc = FontToolsTTFont(font_path, fontNumber=0)
                    # Save as temporary .ttf in fonts directory
                    fonts_dir = Path(__file__).parent / "fonts"
                    fonts_dir.mkdir(exist_ok=True)
                    temp_ttf = fonts_dir / f"extracted_{os.path.basename(font_path).replace('.ttc', '.ttf')}"
                    ttc.save(str(temp_ttf))
                    pdfmetrics.registerFont(TTFont('HindiFont', str(temp_ttf)))
                    print(f"✅ Extracted and registered Hindi font from TTC: {font_path}")
                    font_path = str(temp_ttf)  # Use extracted font for bold
                except ImportError:
                    print(f"⚠️  fonttools not available. Install with: pip install fonttools")
                    print(f"   Or download .ttf font using: python download_hindi_font.py")
                    raise
                except Exception as e:
                    print(f"⚠️  Failed to extract from TTC {font_path}: {e}")
                    continue
            else:
                pdfmetrics.registerFont(TTFont('HindiFont', font_path))
                print(f"✅ Registered Hindi font: {font_path}")
            
            # Try to register bold variant
            bold_path = font_path.replace('Regular', 'Bold').replace('regular', 'bold')
            if os.path.exists(bold_path) and bold_path != font_path:
                if bold_path.endswith('.ttc'):
                    try:
                        pdfmetrics.registerFont(TTFont('HindiFontBold', bold_path))
                    except:
                        # Try extracting from TTC
                        from fontTools.ttLib import TTFont as FontToolsTTFont
                        ttc = FontToolsTTFont(bold_path, fontNumber=0)
                        temp_bold = os.path.join(os.path.dirname(bold_path), 'temp_hindi_font_bold.ttf')
                        ttc.save(temp_bold)
                        pdfmetrics.registerFont(TTFont('HindiFontBold', temp_bold))
                else:
                    pdfmetrics.registerFont(TTFont('HindiFontBold', bold_path))
                print(f"✅ Registered Hindi bold font: {bold_path}")
                return 'HindiFont', 'HindiFontBold'
            else:
                # Use same font for bold (will appear normal weight)
                pdfmetrics.registerFont(TTFont('HindiFontBold', font_path))
                return 'HindiFont', 'HindiFontBold'
        except Exception as e:
            print(f"⚠️  Failed to register {font_path}: {e}")
            continue
    
    # If no fonts found, provide instructions
    print("⚠️  WARNING: No Hindi fonts found. Hindi text may not render correctly.")
    print("   To fix this:")
    print("   1. Run: python backend/documents/download_hindi_font.py")
    print("   2. Or download Noto Sans Devanagari from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
    print("   3. Place the .ttf files in backend/documents/fonts/")
    # Return Helvetica as fallback (will show blocks, but won't crash)
    return 'Helvetica', 'Helvetica-Bold'

HINDI_FONT, HINDI_FONT_BOLD = register_hindi_font()


def replace_rupee_symbol(text):
    """
    Replace rupee symbol (₹) with 'Rs.' for PDF compatibility
    """
    if isinstance(text, str):
        text = re.sub(r'₹', 'Rs.', text)
        text = re.sub(r'Rs\.(\d)', r'Rs. \1', text)
    return text


def create_header_footer(canvas, doc, title):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFillColor(colors.HexColor('#FF8F42'))
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(72, A4[1] - 50, "SUN NATIONAL BANK")
    
    # Title with Hindi font support - use TextObject for better Unicode handling
    canvas.setFillColor(colors.black)
    textobject = canvas.beginText(72, A4[1] - 65)
    try:
        # Try to use Hindi font for title (if it contains Hindi text)
        textobject.setFont(HINDI_FONT_BOLD, 10)
    except:
        # Fallback to regular Hindi font if bold not available
        try:
            textobject.setFont(HINDI_FONT, 10)
        except:
            # Final fallback to Helvetica
            textobject.setFont('Helvetica', 10)
    textobject.textLine(title)
    canvas.drawText(textobject)
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawString(72, 30, "www.sunnationalbank.in | 1800-123-4567 | loans@sunnationalbank.in")
    canvas.drawRightString(A4[0] - 72, 30, f"Page {doc.page}")
    
    canvas.restoreState()


def create_home_loan_doc():
    """Create comprehensive Home Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "home_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles with Hindi font
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    # Title
    story.append(Paragraph("होम लोन", title_style))
    story.append(Paragraph("पूर्ण उत्पाद गाइड और जानकारी", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """
    सन नेशनल बैंक का होम लोन आपको अपना घर खरीदने के सपने को पूरा करने में मदद करने के लिए बनाया गया है। 
    चाहे आप नई प्रॉपर्टी खरीद रहे हों, घर बना रहे हों, या अपने मौजूदा घर का नवीनीकरण कर रहे हों, 
    हम प्रतिस्पर्धी ब्याज दरों और सुविधाजनक चुकौती शर्तों के साथ लचीले वित्तपोषण विकल्प प्रदान करते हैं।
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("मुख्य विशेषताएं", heading_style))
    
    # Create table cell styles with Hindi fonts
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=10, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("विवरण", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph(replace_rupee_symbol("Rs. 5 लाख से Rs. 5 करोड़"), table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("8.35% - 9.50% प्रति वर्ष (फ्लोटिंग रेट)<br/>8.85% - 10.00% प्रति वर्ष (फिक्स्ड रेट)", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("30 वर्ष तक (परिपक्वता पर अधिकतम आयु: 70 वर्ष)", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph(replace_rupee_symbol("लोन राशि का 0.50% (न्यूनतम: Rs. 5,000, अधिकतम: Rs. 25,000) + GST"), table_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", table_cell_style), Paragraph("फ्लोटिंग रेट लोन के लिए शून्य<br/>फिक्स्ड रेट लोन के लिए 2% + GST", table_cell_style)],
        [Paragraph("लोन-टू-वैल्यू अनुपात", table_cell_style), Paragraph(replace_rupee_symbol("Rs. 30 लाख तक के लोन के लिए 90% तक<br/>Rs. 30 लाख से अधिक के लोन के लिए 80% तक"), table_cell_style)],
        [Paragraph("मोरेटोरियम अवधि", table_cell_style), Paragraph("निर्माणाधीन प्रॉपर्टी के लिए 48 महीने तक", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Types of Home Loans
    story.append(Paragraph("होम लोन के प्रकार", heading_style))
    
    story.append(Paragraph("1. होम खरीद लोन", subheading_style))
    story.append(Paragraph("तैयार-रहने-योग्य आवासीय प्रॉपर्टी (नई या पुनर्विक्रय) खरीदने के लिए वित्तपोषण।", normal_style))
    
    story.append(Paragraph("2. होम निर्माण लोन", subheading_style))
    story.append(Paragraph("जमीन के प्लॉट पर घर बनाने के लिए वित्तपोषण जो आपके पास पहले से है। निर्माण प्रगति के आधार पर चरणों में भुगतान किया जाता है।", normal_style))
    
    story.append(Paragraph("3. प्लॉट + निर्माण लोन", subheading_style))
    story.append(Paragraph("प्लॉट खरीदने और उस पर घर बनाने के लिए संयुक्त वित्तपोषण।", normal_style))
    
    story.append(Paragraph("4. होम विस्तार लोन", subheading_style))
    story.append(Paragraph("अपनी मौजूदा आवासीय प्रॉपर्टी का विस्तार या विस्तार करने के लिए वित्तपोषण।", normal_style))
    
    story.append(Paragraph("5. होम नवीनीकरण लोन", subheading_style))
    story.append(Paragraph("अपने मौजूदा घर का नवीनीकरण, मरम्मत या सुधार करने के लिए वित्तपोषण। अधिकतम लोन राशि: Rs. 50 लाख।", normal_style))
    
    story.append(Paragraph("6. बैलेंस ट्रांसफर लोन", subheading_style))
    story.append(Paragraph("बेहतर ब्याज दरों या अतिरिक्त टॉप-अप लोन का लाभ उठाने के लिए दूसरे बैंक से अपना मौजूदा होम लोन सन नेशनल बैंक में स्थानांतरित करें।", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility Criteria
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    
    # Create table cell styles for eligibility table
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("वेतनभोगी व्यक्ति", eligibility_header_style), Paragraph("स्व-नियोजित", eligibility_header_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("21 - 65 वर्ष", eligibility_cell_style), Paragraph("25 - 70 वर्ष", eligibility_cell_style)],
        [Paragraph("न्यूनतम आय", eligibility_cell_style), Paragraph("Rs. 25,000 प्रति माह", eligibility_cell_style), Paragraph("Rs. 3,00,000 प्रति वर्ष", eligibility_cell_style)],
        [Paragraph("काम का अनुभव", eligibility_cell_style), Paragraph("न्यूनतम 2 वर्ष (वर्तमान संगठन में 1 वर्ष)", eligibility_cell_style), Paragraph("व्यवसाय में न्यूनतम 3 वर्ष", eligibility_cell_style)],
        [Paragraph("क्रेडिट स्कोर", eligibility_cell_style), Paragraph("न्यूनतम 700 (CIBIL)", eligibility_cell_style), Paragraph("न्यूनतम 700 (CIBIL)", eligibility_cell_style)],
        [Paragraph("रोजगार प्रकार", eligibility_cell_style), Paragraph("प्रतिष्ठित संगठन के साथ स्थायी कर्मचारी", eligibility_cell_style), Paragraph("पिछले 3 वर्षों से ITR दाखिल करने वाला स्थिर व्यवसाय", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Documents Required
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    
    story.append(Paragraph("वेतनभोगी आवेदकों के लिए:", subheading_style))
    salaried_docs = [
        "• फोटो के साथ पूर्ण लोन आवेदन फॉर्म",
        "• पहचान प्रमाण: PAN कार्ड, आधार कार्ड, पासपोर्ट, वोटर ID, या ड्राइविंग लाइसेंस",
        "• पता प्रमाण: आधार कार्ड, पासपोर्ट, उपयोगिता बिल, या किराया समझौता",
        "• आयु प्रमाण: जन्म प्रमाणपत्र, PAN कार्ड, या पासपोर्ट",
        "• आय प्रमाण: पिछले 6 महीने के वेतन स्लिप और बैंक स्टेटमेंट",
        "• पिछले 2 वर्षों के लिए Form 16 या IT रिटर्न",
        "• रोजगार प्रमाण: रोजगार पत्र या अनुबंध",
        "• प्रॉपर्टी दस्तावेज: बिक्री दस्तावेज, अनुमोदित भवन योजना, सोसाइटी से NOC",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("स्व-नियोजित आवेदकों के लिए:", subheading_style))
    self_emp_docs = [
        "• वेतनभोगी व्यक्तियों के लिए उपरोक्त सभी दस्तावेज",
        "• व्यवसाय प्रमाण: व्यवसाय पंजीकरण प्रमाणपत्र, GST पंजीकरण, साझेदारी दस्तावेज",
        "• आय गणना के साथ पिछले 3 वर्षों के आयकर रिटर्न",
        "• पिछले 3 वर्षों के लेखा परीक्षित बैलेंस शीट और लाभ और हानि विवरण",
        "• पिछले 12 महीने के बैंक स्टेटमेंट (व्यवसाय खाता)",
        "• चुकौती ट्रैक रिकॉर्ड के साथ मौजूदा व्यवसाय लोन की सूची",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # EMI Calculation Example
    story.append(Paragraph("EMI गणना उदाहरण", heading_style))
    emi_examples_text = """
    EMI (समान मासिक किस्त) की गणना निम्न सूत्र का उपयोग करके की जाती है:<br/>
    <b>EMI = [P x R x (1+R)^N] / [(1+R)^N-1]</b><br/>
    जहां: P = मूल लोन राशि, R = मासिक ब्याज दर, N = महीनों की संख्या
    """
    story.append(Paragraph(emi_examples_text, normal_style))
    
    # Create table cell styles for EMI table
    emi_header_style = ParagraphStyle('EMIHeader', parent=styles['Normal'],
                                     fontSize=7, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_CENTER)
    emi_cell_style = ParagraphStyle('EMICell', parent=styles['Normal'],
                                   fontSize=7, fontName=HINDI_FONT,
                                   alignment=TA_CENTER)
    
    emi_data = [
        [Paragraph("लोन राशि", emi_header_style), Paragraph("ब्याज दर", emi_header_style), Paragraph("अवधि", emi_header_style), Paragraph("मासिक EMI", emi_header_style), Paragraph("कुल ब्याज", emi_header_style), Paragraph("कुल भुगतान", emi_header_style)],
        [Paragraph("Rs. 25,00,000", emi_cell_style), Paragraph("8.50% प्रति वर्ष", emi_cell_style), Paragraph("20 वर्ष", emi_cell_style), Paragraph("Rs. 21,612", emi_cell_style), Paragraph("Rs. 26,86,880", emi_cell_style), Paragraph("Rs. 51,86,880", emi_cell_style)],
        [Paragraph("Rs. 50,00,000", emi_cell_style), Paragraph("8.50% प्रति वर्ष", emi_cell_style), Paragraph("25 वर्ष", emi_cell_style), Paragraph("Rs. 39,712", emi_cell_style), Paragraph("Rs. 69,13,600", emi_cell_style), Paragraph("Rs. 1,19,13,600", emi_cell_style)],
        [Paragraph("Rs. 75,00,000", emi_cell_style), Paragraph("9.00% प्रति वर्ष", emi_cell_style), Paragraph("30 वर्ष", emi_cell_style), Paragraph("Rs. 60,347", emi_cell_style), Paragraph("Rs. 1,42,24,920", emi_cell_style), Paragraph("Rs. 2,17,24,920", emi_cell_style)],
        [Paragraph("Rs. 1,00,00,000", emi_cell_style), Paragraph("9.00% प्रति वर्ष", emi_cell_style), Paragraph("20 वर्ष", emi_cell_style), Paragraph("Rs. 89,973", emi_cell_style), Paragraph("Rs. 1,15,93,520", emi_cell_style), Paragraph("Rs. 2,15,93,520", emi_cell_style)],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Special Benefits
    story.append(Paragraph("विशेष लाभ और ऑफर", heading_style))
    benefits = [
        "• <b>महिला उधारकर्ता:</b> महिला आवेदकों के लिए ब्याज दर में 0.05% छूट",
        "• <b>कोई छुपी हुई फीस नहीं:</b> सभी शुल्क और चार्ज में पूर्ण पारदर्शिता",
        "• <b>त्वरित अनुमोदन:</b> 48 घंटों के भीतर सिद्धांत अनुमोदन",
        "• <b>लचीली चुकौती:</b> आय बढ़ने पर EMI बढ़ाने का विकल्प (Step-up EMI)",
        "• <b>टैक्स लाभ:</b> मूलधन पर Rs. 1.5 लाख तक कटौती (Sec 80C) + ब्याज पर Rs. 2 लाख (Sec 24)",
        "• <b>मुफ्त बीमा:</b> पहले वर्ष के लिए निःशुल्क प्रॉपर्टी बीमा",
        "• <b>डोरस्टेप सेवा:</b> आपकी सुविधा के अनुसार दस्तावेज पिकअप और डिलीवरी",
        "• <b>डिजिटल प्रक्रिया:</b> मोबाइल ऐप या वेबसाइट के माध्यम से पेपरलेस लोन आवेदन",
    ]
    for benefit in benefits:
        story.append(Paragraph(benefit, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Fees and Charges
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("लोन राशि का 0.50% (न्यूनतम Rs. 5,000, अधिकतम Rs. 25,000) + GST", fees_cell_style)],
        [Paragraph("लॉगिन शुल्क/दस्तावेज शुल्क", fees_cell_style), Paragraph("Rs. 5,000 + GST (एक बार)", fees_cell_style)],
        [Paragraph("प्रॉपर्टी मूल्यांकन शुल्क", fees_cell_style), Paragraph("वास्तविक लागत (Rs. 3,000 - Rs. 10,000 प्रॉपर्टी के आधार पर)", fees_cell_style)],
        [Paragraph("कानूनी और तकनीकी शुल्क", fees_cell_style), Paragraph("Rs. 5,000 - Rs. 15,000 + GST", fees_cell_style)],
        [Paragraph("स्टाम्प ड्यूटी और पंजीकरण", fees_cell_style), Paragraph("राज्य सरकार के मानदंडों के अनुसार (ग्राहक के खाते में)", fees_cell_style)],
        [Paragraph("देर से भुगतान जुर्माना", fees_cell_style), Paragraph("बकाया राशि पर प्रति माह 2%", fees_cell_style)],
        [Paragraph("चेक/NACH बाउंस शुल्क", fees_cell_style), Paragraph("प्रति उदाहरण Rs. 500", fees_cell_style)],
        [Paragraph("आंशिक पूर्व भुगतान शुल्क (फ्लोटिंग)", fees_cell_style), Paragraph("शून्य", fees_cell_style)],
        [Paragraph("आंशिक पूर्व भुगतान शुल्क (फिक्स्ड)", fees_cell_style), Paragraph("पूर्व भुगतान राशि का 2% + GST", fees_cell_style)],
        [Paragraph("फोरक्लोजर शुल्क (फ्लोटिंग)", fees_cell_style), Paragraph("शून्य", fees_cell_style)],
        [Paragraph("फोरक्लोजर शुल्क (फिक्स्ड)", fees_cell_style), Paragraph("बकाया मूलधन का 3% + GST", fees_cell_style)],
        [Paragraph("लोन रद्दीकरण शुल्क", fees_cell_style), Paragraph("Rs. 5,000 + GST (अनुमोदन के बाद रद्द करने पर)", fees_cell_style)],
        [Paragraph("डुप्लिकेट स्टेटमेंट शुल्क", fees_cell_style), Paragraph("प्रति स्टेटमेंट Rs. 250", fees_cell_style)],
        [Paragraph("NOC/क्लोजर सर्टिफिकेट", fees_cell_style), Paragraph("Rs. 1,000 + GST", fees_cell_style)],
        [Paragraph("स्वैप शुल्क (फिक्स्ड से फ्लोटिंग)", fees_cell_style), Paragraph("बकाया मूलधन का 0.50% + GST", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[3.5*inch, 3*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    # Loan Process
    story.append(Paragraph("लोन आवेदन प्रक्रिया", heading_style))
    
    process_steps = [
        ("<b>चरण 1: आवेदन</b>", "ऑनलाइन लोन आवेदन जमा करें या निकटतम शाखा पर जाएं। बुनियादी विवरण प्रदान करें और दस्तावेज अपलोड करें।"),
        ("<b>चरण 2: दस्तावेज सत्यापन</b>", "हमारी टीम आपके दस्तावेजों को सत्यापित करती है और आय मूल्यांकन करती है। आमतौर पर 2 कार्य दिवसों के भीतर पूरा होता है।"),
        ("<b>चरण 3: प्रॉपर्टी मूल्यांकन</b>", "प्रॉपर्टी का तकनीकी और कानूनी सत्यापन हमारे पैनल वैल्यूअर्स द्वारा किया जाता है।"),
        ("<b>चरण 4: क्रेडिट मूल्यांकन</b>", "आपका क्रेडिट इतिहास, चुकौती क्षमता और पात्रता का मूल्यांकन हमारी क्रेडिट टीम द्वारा किया जाता है।"),
        ("<b>चरण 5: अनुमोदन</b>", "अनुमोदित लोन राशि, ब्याज दर और शर्तों के साथ लोन अनुमोदन पत्र जारी किया जाता है।"),
        ("<b>चरण 6: कानूनी दस्तावेजीकरण</b>", "लोन समझौता, मॉर्गेज डीड और अन्य कानूनी दस्तावेज निष्पादित किए जाते हैं।"),
        ("<b>चरण 7: भुगतान</b>", "भुगतान अनुसूची के अनुसार लोन राशि सीधे विक्रेता/बिल्डर को भुगतान की जाती है।"),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    
    faqs = [
        ("<b>Q1: मुझे अधिकतम कितनी लोन राशि मिल सकती है?</b>",
         "अधिकतम लोन राशि आपकी आय, आयु, मौजूदा दायित्वों और प्रॉपर्टी मूल्य पर निर्भर करती है। आम तौर पर, हम पात्र ग्राहकों के लिए Rs. 5 करोड़ तक प्रदान करते हैं।"),
        
        ("<b>Q2: क्या मैं अपने होम लोन का पूर्व भुगतान कर सकता हूं?</b>",
         "हां, आप कभी भी अपने होम लोन का पूर्व भुगतान कर सकते हैं। फ्लोटिंग रेट लोन के लिए, कोई पूर्व भुगतान शुल्क नहीं है। फिक्स्ड रेट लोन के लिए, पूर्व भुगतान राशि पर 2% + GST लिया जाता है।"),
        
        ("<b>Q3: फिक्स्ड और फ्लोटिंग ब्याज दरों में क्या अंतर है?</b>",
         "फिक्स्ड रेट लोन अवधि के दौरान स्थिर रहता है, जबकि फ्लोटिंग रेट बाजार की स्थितियों और RBI नीति परिवर्तनों के आधार पर भिन्न होता है। फ्लोटिंग दरें आम तौर पर फिक्स्ड दरों से 0.50% कम होती हैं।"),
        
        ("<b>Q4: मेरी पात्रता की गणना कैसे की जाती है?</b>",
         "पात्रता आपकी मासिक आय, आयु, क्रेडिट स्कोर, मौजूदा दायित्वों और प्रॉपर्टी मूल्य पर आधारित है। एक सामान्य नियम के रूप में, आपकी EMI आपकी शुद्ध मासिक आय के 50% से अधिक नहीं होनी चाहिए।"),
        
        ("<b>Q5: मोरेटोरियम अवधि क्या है?</b>",
         "निर्माणाधीन प्रॉपर्टी के लिए, आप मोरेटोरियम अवधि (pre-EMI) चुन सकते हैं जहां आप निर्माण के दौरान केवल ब्याज का भुगतान करते हैं। कब्जा मिलने के बाद पूर्ण EMI शुरू होती है।"),
        
        ("<b>Q6: क्या मैं संयुक्त होम लोन प्राप्त कर सकता हूं?</b>",
         "हां, आप पति/पत्नी, माता-पिता या भाई-बहनों के साथ संयुक्त रूप से आवेदन कर सकते हैं। संयुक्त लोन पात्रता बढ़ाते हैं और दोनों आवेदक कर लाभ का दावा कर सकते हैं।"),
        
        ("<b>Q7: कौन सा बीमा आवश्यक है?</b>",
         "आग, भूकंप और प्राकृतिक आपदाओं से सुरक्षा के लिए प्रॉपर्टी बीमा अनिवार्य है। उधारकर्ता का जीवन बीमा अनुशंसित है लेकिन अनिवार्य नहीं है।"),
        
        ("<b>Q8: अनुमोदन प्रक्रिया में कितना समय लगता है?</b>",
         "दस्तावेज जमा करने के 48 घंटों के भीतर सिद्धांत अनुमोदन दिया जाता है। प्रॉपर्टी सत्यापन के साथ पूर्ण अनुमोदन में 7-10 कार्य दिवस लगते हैं।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Important Notes
    story.append(Paragraph("महत्वपूर्ण नोट्स", heading_style))
    notes = [
        "• उल्लिखित ब्याज दरें और शुल्क RBI दिशानिर्देशों और बैंक की नीति के आधार पर परिवर्तन के अधीन हैं।",
        "• लोन अनुमोदन क्रेडिट मूल्यांकन, प्रॉपर्टी मूल्यांकन और सत्यापन के अधीन है।",
        "• लोन की पूर्ण चुकौती तक प्रॉपर्टी बैंक के पास गिरवी रहती है।",
        "• EMI ऑटो-डेबिट (NACH), पोस्ट-डेटेड चेक या ऑनलाइन ट्रांसफर के माध्यम से भुगतान किया जा सकता है।",
        "• लोन खाते क्रेडिट ब्यूरो (CIBIL, Experian, CRIF, Equifax) को रिपोर्ट किए जाएंगे।",
        "• NRI ग्राहकों के लिए, अतिरिक्त दस्तावेजीकरण और FEMA अनुपालन आवश्यक है।",
        "• वरिष्ठ नागरिक (60 वर्ष से अधिक) को विशेष ब्याज दर छूट मिल सकती है जो 0.25% तक हो सकती है।",
        "• बैलेंस ट्रांसफर ग्राहकों का कम से कम 12 महीने तक अच्छा चुकौती ट्रैक रिकॉर्ड होना चाहिए।",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    contact_text = """<para align=center><b>होम लोन के लिए</b><br/>कस्टमर केयर: 1800-123-4567<br/>ईमेल: homeloan@sunnationalbank.in<br/>वेबसाइट: www.sunnationalbank.in/home-loan</para>"""
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "होम लोन गाइड"), 
              onLaterPages=lambda c, d: create_header_footer(c, d, "होम लोन गाइड"))
    return output_path


# Similar functions for other loan types - creating simplified versions
def create_personal_loan_doc():
    """Create comprehensive Personal Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "personal_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("पर्सनल लोन", title_style))
    story.append(Paragraph("आपकी सभी जरूरतों के लिए तत्काल वित्तीय समाधान", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """
    सन नेशनल बैंक पर्सनल लोन आपकी तत्काल वित्तीय जरूरतों को पूरा करने के लिए डिज़ाइन किया गया एक असुरक्षित लोन है - 
    चाहे वह चिकित्सा आपातकाल, शादी के खर्च, यात्रा, घर का नवीनीकरण, या कोई अन्य व्यक्तिगत आवश्यकता हो। 
    न्यूनतम दस्तावेजीकरण और लचीले चुकौती विकल्पों के साथ तत्काल अनुमोदन प्राप्त करें।
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("मुख्य विशेषताएं", heading_style))
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=10, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("विवरण", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("Rs. 50,000 से Rs. 25 लाख", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("10.49% - 18.00% प्रति वर्ष (क्रेडिट प्रोफ़ाइल के आधार पर)", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("12 से 60 महीने (1 से 5 वर्ष)", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("लोन राशि का 2% तक + GST", table_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", table_cell_style), Paragraph("6 महीने के बाद शून्य<br/>6 महीने के भीतर पूर्व भुगतान करने पर 4% + GST", table_cell_style)],
        [Paragraph("दस्तावेजीकरण", table_cell_style), Paragraph("न्यूनतम - KYC, आय प्रमाण और बैंक स्टेटमेंट", table_cell_style)],
        [Paragraph("अनुमोदन समय", table_cell_style), Paragraph("तत्काल सिद्धांत अनुमोदन*<br/>24 घंटों के भीतर भुगतान", table_cell_style)],
        [Paragraph("गारंटी आवश्यक", table_cell_style), Paragraph("कोई गारंटी या सुरक्षा आवश्यक नहीं", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Paragraph("*अच्छे क्रेडिट स्कोर वाले पूर्व-अनुमोदित ग्राहकों के लिए", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("वेतनभोगी", eligibility_header_style), Paragraph("स्व-नियोजित", eligibility_header_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("21 - 60 वर्ष", eligibility_cell_style), Paragraph("25 - 65 वर्ष", eligibility_cell_style)],
        [Paragraph("न्यूनतम आय", eligibility_cell_style), Paragraph("Rs. 20,000 प्रति माह", eligibility_cell_style), Paragraph("Rs. 2,50,000 प्रति वर्ष (ITR)", eligibility_cell_style)],
        [Paragraph("काम का अनुभव", eligibility_cell_style), Paragraph("न्यूनतम 1 वर्ष (वर्तमान कंपनी में 6 महीने)", eligibility_cell_style), Paragraph("व्यवसाय में न्यूनतम 2 वर्ष", eligibility_cell_style)],
        [Paragraph("क्रेडिट स्कोर (CIBIL)", eligibility_cell_style), Paragraph("सर्वोत्तम दरों के लिए न्यूनतम 750<br/>650-749: उच्च ब्याज<br/>650 से नीचे: अस्वीकृत हो सकता है", eligibility_cell_style), Paragraph("सर्वोत्तम दरों के लिए न्यूनतम 750<br/>650-749: उच्च ब्याज<br/>650 से नीचे: अस्वीकृत हो सकता है", eligibility_cell_style)],
        [Paragraph("राष्ट्रीयता", eligibility_cell_style), Paragraph("भारतीय निवासी या NRI", eligibility_cell_style), Paragraph("भारतीय निवासी या NRI", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[2*inch, 2.2*inch, 2.3*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Documents Required
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    story.append(Paragraph("वेतनभोगी व्यक्तियों के लिए:", subheading_style))
    salaried_docs = [
        "• पहचान प्रमाण: आधार कार्ड, PAN कार्ड, पासपोर्ट, या वोटर ID",
        "• पता प्रमाण: आधार, उपयोगिता बिल (3 महीने से पुराना नहीं), पासपोर्ट",
        "• आय प्रमाण: पिछले 3 महीने के वेतन स्लिप",
        "• बैंक स्टेटमेंट: वेतन क्रेडिट दिखाने वाला पिछले 6 महीने का स्टेटमेंट",
        "• रोजगार प्रमाण: रोजगार प्रमाणपत्र या ऑफर लेटर",
        "• फोटो: 2 हाल की पासपोर्ट साइज फोटो",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("स्व-नियोजित व्यक्तियों के लिए:", subheading_style))
    self_emp_docs = [
        "• पहचान प्रमाण: आधार कार्ड, PAN कार्ड (अनिवार्य)",
        "• पता प्रमाण: आधार, उपयोगिता बिल, प्रॉपर्टी दस्तावेज",
        "• व्यवसाय प्रमाण: GST पंजीकरण, व्यवसाय पंजीकरण प्रमाणपत्र, दुकान लाइसेंस",
        "• आय प्रमाण: आय गणना के साथ पिछले 2 वर्षों के IT रिटर्न",
        "• बैंक स्टेटमेंट: पिछले 12 महीने का व्यवसाय खाता स्टेटमेंट",
        "• वित्तीय विवरण: पिछले 2 वर्षों के लिए बैलेंस शीट और P&L (यदि उपलब्ध हो)",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # Interest Rate Structure
    story.append(Paragraph("ब्याज दर संरचना", heading_style))
    rate_info = """
    ब्याज दरें आपके क्रेडिट प्रोफ़ाइल, आय स्थिरता और बैंक के साथ मौजूदा संबंध के आधार पर निर्धारित की जाती हैं।
    """
    story.append(Paragraph(rate_info, normal_style))
    
    rate_header_style = ParagraphStyle('RateHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_CENTER)
    rate_cell_style = ParagraphStyle('RateCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_CENTER)
    
    rate_data = [
        [Paragraph("CIBIL स्कोर", rate_header_style), Paragraph("ब्याज दर (प्रति वर्ष)", rate_header_style), Paragraph("प्रोसेसिंग शुल्क", rate_header_style)],
        [Paragraph("750 और उससे अधिक (उत्कृष्ट)", rate_cell_style), Paragraph("10.49% - 12.99%", rate_cell_style), Paragraph("लोन राशि का 1%", rate_cell_style)],
        [Paragraph("700 - 749 (अच्छा)", rate_cell_style), Paragraph("13.00% - 14.99%", rate_cell_style), Paragraph("लोन राशि का 1.5%", rate_cell_style)],
        [Paragraph("650 - 699 (सामान्य)", rate_cell_style), Paragraph("15.00% - 16.99%", rate_cell_style), Paragraph("लोन राशि का 2%", rate_cell_style)],
        [Paragraph("600 - 649 (खराब)", rate_cell_style), Paragraph("17.00% - 18.00%", rate_cell_style), Paragraph("लोन राशि का 2%", rate_cell_style)],
        [Paragraph("600 से नीचे", rate_cell_style), Paragraph("लोन अनुमोदित नहीं हो सकता", rate_cell_style), Paragraph("-", rate_cell_style)],
    ]
    
    rate_table = Table(rate_data, colWidths=[2*inch, 2.5*inch, 2*inch])
    rate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rate_table)
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI गणना उदाहरण", heading_style))
    emi_header_style = ParagraphStyle('EMIHeader', parent=styles['Normal'],
                                     fontSize=8, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_CENTER)
    emi_cell_style = ParagraphStyle('EMICell', parent=styles['Normal'],
                                   fontSize=7, fontName=HINDI_FONT,
                                   alignment=TA_CENTER)
    
    emi_data = [
        [Paragraph("लोन राशि", emi_header_style), Paragraph("ब्याज दर", emi_header_style), Paragraph("अवधि", emi_header_style), Paragraph("मासिक EMI", emi_header_style), Paragraph("कुल ब्याज", emi_header_style), Paragraph("कुल भुगतान", emi_header_style)],
        [Paragraph("Rs. 2,00,000", emi_cell_style), Paragraph("11.00%", emi_cell_style), Paragraph("24 महीने", emi_cell_style), Paragraph("Rs. 9,284", emi_cell_style), Paragraph("Rs. 22,816", emi_cell_style), Paragraph("Rs. 2,22,816", emi_cell_style)],
        [Paragraph("Rs. 5,00,000", emi_cell_style), Paragraph("12.00%", emi_cell_style), Paragraph("36 महीने", emi_cell_style), Paragraph("Rs. 16,607", emi_cell_style), Paragraph("Rs. 97,852", emi_cell_style), Paragraph("Rs. 5,97,852", emi_cell_style)],
        [Paragraph("Rs. 10,00,000", emi_cell_style), Paragraph("13.00%", emi_cell_style), Paragraph("48 महीने", emi_cell_style), Paragraph("Rs. 26,783", emi_cell_style), Paragraph("Rs. 12,85,584", emi_cell_style), Paragraph("Rs. 22,85,584", emi_cell_style)],
        [Paragraph("Rs. 15,00,000", emi_cell_style), Paragraph("14.00%", emi_cell_style), Paragraph("60 महीने", emi_cell_style), Paragraph("Rs. 34,865", emi_cell_style), Paragraph("Rs. 20,91,900", emi_cell_style), Paragraph("Rs. 35,91,900", emi_cell_style)],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.1*inch, 1*inch, 1*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Fees and Charges
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("लोन राशि का 2% तक + GST", fees_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", fees_cell_style), Paragraph("6 EMI भुगतान के बाद शून्य<br/>6 महीने के भीतर मूलधन बकाया का 4% + GST", fees_cell_style)],
        [Paragraph("फोरक्लोजर शुल्क", fees_cell_style), Paragraph("12 EMI भुगतान के बाद शून्य<br/>12 महीने के भीतर बकाया का 5% + GST", fees_cell_style)],
        [Paragraph("देर से भुगतान शुल्क", fees_cell_style), Paragraph("बकाया राशि पर प्रति माह 2% या Rs. 500, जो भी अधिक हो", fees_cell_style)],
        [Paragraph("चेक/NACH बाउंस", fees_cell_style), Paragraph("प्रति उदाहरण Rs. 500", fees_cell_style)],
        [Paragraph("लोन रद्दीकरण", fees_cell_style), Paragraph("Rs. 3,000 + GST (अनुमोदन के बाद लेकिन भुगतान से पहले)", fees_cell_style)],
        [Paragraph("स्टेटमेंट अनुरोध", fees_cell_style), Paragraph("प्रति स्टेटमेंट Rs. 100", fees_cell_style)],
        [Paragraph("डुप्लिकेट NOC", fees_cell_style), Paragraph("Rs. 500 + GST", fees_cell_style)],
        [Paragraph("EMI स्वैप शुल्क", fees_cell_style), Paragraph("प्रति स्वैप Rs. 500 + GST", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    # Loan Process
    story.append(Paragraph("लोन आवेदन प्रक्रिया", heading_style))
    process_steps = [
        ("<b>चरण 1: ऑनलाइन/ऑफलाइन आवेदन करें</b>", "मोबाइल ऐप, वेबसाइट के माध्यम से आवेदन जमा करें या शाखा पर जाएं। बुनियादी KYC और आय विवरण प्रदान करें।"),
        ("<b>चरण 2: दस्तावेज अपलोड</b>", "आवश्यक दस्तावेज डिजिटल रूप से अपलोड करें या शाखा पर जमा करें। हमारी टीम 2 घंटों के भीतर सत्यापित करेगी।"),
        ("<b>चरण 3: क्रेडिट मूल्यांकन</b>", "आपके क्रेडिट स्कोर, आय और चुकौती क्षमता का मूल्यांकन किया जाता है। पूर्व-अनुमोदित ग्राहकों के लिए तत्काल निर्णय।"),
        ("<b>चरण 4: अनुमोदन और अनुमोदन</b>", "अनुमोदित राशि, ब्याज दर, अवधि और EMI विवरण के साथ अनुमोदन पत्र SMS और ईमेल के माध्यम से प्राप्त करें।"),
        ("<b>चरण 5: समझौता हस्ताक्षर</b>", "लोन समझौते को डिजिटल रूप से ई-साइन करें या भौतिक हस्ताक्षर के लिए शाखा पर जाएं। आधार ई-साइन स्वीकार किया जाता है।"),
        ("<b>चरण 6: भुगतान</b>", "समझौता हस्ताक्षर के 24 घंटों के भीतर लोन राशि सीधे आपके बैंक खाते में जमा की जाती है।"),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Special Features
    story.append(Paragraph("विशेष सुविधाएं और लाभ", heading_style))
    benefits = [
        "• <b>तत्काल भुगतान:</b> तत्काल जरूरतों के लिए 24 घंटों के भीतर अपने खाते में पैसा प्राप्त करें",
        "• <b>लचीली अवधि:</b> अपने बजट के अनुसार 12 से 60 महीने तक EMI अवधि चुनें",
        "• <b>कोई गारंटी नहीं:</b> पूरी तरह से असुरक्षित लोन - किसी भी संपत्ति को गिरवी रखने की आवश्यकता नहीं",
        "• <b>न्यूनतम दस्तावेजीकरण:</b> केवल बुनियादी KYC और आय प्रमाण आवश्यक",
        "• <b>मुफ्त पूर्व भुगतान:</b> 6 महीने के बाद कभी भी शून्य शुल्क के साथ अपना लोन बंद करें",
        "• <b>मौजूदा ग्राहक लाभ:</b> मौजूदा खाता धारकों के लिए विशेष दरें और तत्काल अनुमोदन",
        "• <b>टॉप-अप सुविधा:</b> 6 महीने के बाद मौजूदा पर्सनल लोन पर अतिरिक्त लोन प्राप्त करें",
        "• <b>EMI मोरेटोरियम:</b> पहली EMI को 1 महीने तक स्थगित करने का विकल्प (ब्याज लागू)",
        "• <b>बीमा विकल्प:</b> अपने परिवार को सुरक्षित करने के लिए EMI सुरक्षा बीमा चुनें",
        "• <b>डिजिटल यात्रा:</b> मोबाइल ऐप के माध्यम से पूर्ण पेपरलेस प्रक्रिया",
    ]
    
    for benefit in benefits:
        story.append(Paragraph(benefit, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: मैं पर्सनल लोन का उपयोग किसके लिए कर सकता हूं?</b>",
         "पर्सनल लोन का उपयोग किसी भी वैध उद्देश्य के लिए किया जा सकता है - चिकित्सा आपातकाल, शादी, यात्रा, शिक्षा, घर का नवीनीकरण, ऋण समेकन, या कोई अन्य व्यक्तिगत आवश्यकता। कोई अंत-उपयोग प्रतिबंध नहीं।"),
        
        ("<b>Q2: मेरी लोन राशि पात्रता की गणना कैसे की जाती है?</b>",
         "पात्रता आपकी मासिक आय, क्रेडिट स्कोर, मौजूदा दायित्वों और आयु पर आधारित है। आम तौर पर, आपकी कुल EMI (नए लोन सहित) आपकी मासिक आय के 50-60% से अधिक नहीं होनी चाहिए।"),
        
        ("<b>Q3: क्या मैं कम CIBIL स्कोर के साथ लोन प्राप्त कर सकता हूं?</b>",
         "न्यूनतम CIBIL स्कोर 650 आवश्यक है। हालांकि, बेहतर स्कोर (750+) को कम ब्याज दरें और तेज अनुमोदन मिलता है। 650 से नीचे, लोन अस्वीकृत हो सकता है या उच्च दरों पर पेश किया जा सकता है।"),
        
        ("<b>Q4: मुझे लोन राशि कितनी जल्दी मिलेगी?</b>",
         "अच्छे क्रेडिट वाले पूर्व-अनुमोदित ग्राहकों के लिए, तत्काल अनुमोदन और 24 घंटों के भीतर भुगतान। नए ग्राहकों के लिए, दस्तावेज सत्यापन के बाद 2-3 कार्य दिवस।"),
        
        ("<b>Q5: क्या मैं अपने पर्सनल लोन का पूर्व भुगतान कर सकता हूं?</b>",
         "हां, आप कभी भी पूर्व भुगतान कर सकते हैं। यदि आप 6 महीने के बाद पूर्व भुगतान करते हैं तो कोई शुल्क नहीं है। पहले 6 महीने के भीतर पूर्व भुगतान करने पर 4% + GST।"),
        
        ("<b>Q6: यदि मैं EMI भुगतान चूक जाऊं तो क्या होगा?</b>",
         "बकाया राशि पर प्रति माह 2% या Rs. 500 (जो भी अधिक हो) का देर से भुगतान शुल्क लगाया जाएगा। यह आपके क्रेडिट स्कोर को भी नकारात्मक रूप से प्रभावित करेगा। यदि कठिनाई का सामना कर रहे हैं तो तुरंत हमसे संपर्क करें।"),
        
        ("<b>Q7: क्या मैं भुगतान के बाद अपनी लोन राशि बढ़ा सकता हूं?</b>",
         "हां, आप 6 EMI सफलतापूर्वक भुगतान करने के बाद टॉप-अप लोन के लिए आवेदन कर सकते हैं। टॉप-अप राशि आपके चुकौती ट्रैक रिकॉर्ड और आय पर निर्भर करती है।"),
        
        ("<b>Q8: क्या पर्सनल लोन पर आयकर लाभ उपलब्ध है?</b>",
         "नहीं, पर्सनल लोन आयकर अधिनियम के तहत कोई कर लाभ प्रदान नहीं करता है। केवल होम लोन, शिक्षा लोन और व्यवसाय लोन कर कटौती के लिए पात्र हैं।"),
        
        ("<b>Q9: क्या मैं दूसरे बैंक से अपना पर्सनल लोन स्थानांतरित कर सकता हूं?</b>",
         "हां, बैलेंस ट्रांसफर स्वीकार किया जाता है यदि आपने अपने वर्तमान ऋणदाता को कम से कम 6 EMI का भुगतान किया है और आपका अच्छा चुकौती ट्रैक रिकॉर्ड है। 1% + GST का प्रोसेसिंग शुल्क लागू होता है।"),
        
        ("<b>Q10: स्व-नियोजित के लिए कौन से दस्तावेज चाहिए?</b>",
         "स्व-नियोजित व्यक्तियों को चाहिए: PAN कार्ड, आधार, व्यवसाय प्रमाण (GST/दुकान लाइसेंस), आय गणना के साथ पिछले 2 वर्षों के ITR, और नियमित व्यवसाय लेनदेन दिखाने वाला 12 महीने का बैंक स्टेटमेंट।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Important Terms
    story.append(Paragraph("महत्वपूर्ण नियम और शर्तें", heading_style))
    terms = [
        "• पर्सनल लोन क्रेडिट मूल्यांकन और बैंक के विवेक के अधीन एक असुरक्षित क्रेडिट सुविधा है।",
        "• ब्याज दर एक बार अनुमोदित होने के बाद पूरी अवधि के लिए निश्चित होती है।",
        "• EMI तिथि आपकी वेतन तिथि के आधार पर चुनी जा सकती है (महीने की 1 से 28 तक कोई भी तारीख)।",
        "• लोन सभी क्रेडिट ब्यूरो (CIBIL, Experian, CRIF, Equifax) को रिपोर्ट किया जाएगा। समय पर भुगतान सुनिश्चित करें।",
        "• यदि आप 3 लगातार EMI पर चूक करते हैं तो बैंक को पूरे लोन को वापस बुलाने का अधिकार है।",
        "• गलत जानकारी या दस्तावेज प्रदान करना एक आपराधिक अपराध है और लोन तुरंत रद्द कर दिया जाएगा।",
        "• NRI ग्राहकों के लिए: NRO/NRE खाता आवश्यक, FEMA अनुपालन अनिवार्य, दरें भिन्न हो सकती हैं।",
        "• बीमा (EMI सुरक्षा) वैकल्पिक है और लोन अनुमोदन के लिए अनिवार्य नहीं है।",
        "• लोन राशि केवल आपके बैंक खाते में भुगतान की जाएगी - नकद भुगतान की अनुमति नहीं है।",
        "• पूर्व भुगतान/फोरक्लोजर अनुरोध आवश्यक राशि के साथ 7 दिन पहले जमा करना होगा।",
        "• प्रोसेसिंग शुल्क गैर-वापसी योग्य है भले ही लोन अस्वीकृत हो या ग्राहक द्वारा रद्द किया गया हो।",
        "• उल्लिखित सभी शुल्क और चार्ज प्रचलित दरों के अनुसार GST के अधीन हैं।",
        "• बैंक वसूली और ग्राहक व्यवहार के लिए RBI दिशानिर्देशों के अनुसार निष्पक्ष अभ्यास संहिता का पालन करता है।",
        "• शिकायत निवारण: यदि हल नहीं हुआ तो ग्राहक सेवा से संपर्क करें या बैंकिंग ओम्बड्समैन से संपर्क करें।",
    ]
    
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>लोन सहायता और प्रश्नों के लिए</b><br/>
    कस्टमर केयर: 1800-123-4567 (टोल फ्री) | 080-1234-5678<br/>
    ईमेल: loans@sunnationalbank.in | personalloans@sunnationalbank.in<br/>
    वेबसाइट: www.sunnationalbank.in/personal-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>अपनी निकटतम सन नेशनल बैंक शाखा पर जाएं या 24x7 ऑनलाइन आवेदन करें</i>
    </para>
    """
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "पर्सनल लोन गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "पर्सनल लोन गाइड"))
    
    return output_path


# Simplified versions for other loan types - you can expand these similarly
def create_auto_loan_doc():
    """Create comprehensive Auto Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "auto_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("ऑटो लोन", title_style))
    story.append(Paragraph("अपने सपनों को घर ले जाएं - कारें, बाइक और वाणिज्यिक वाहन", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """
    सन नेशनल बैंक ऑटो लोन आपको अपना सपनों का वाहन खरीदने में मदद करता है - नई या पुरानी कारें, दोपहिया वाहन, या वाणिज्यिक वाहन। 
    प्रतिस्पर्धी ब्याज दरों, 7 वर्ष तक लचीली अवधि और परेशानी-मुक्त प्रसंस्करण के साथ, हम वाहन स्वामित्व को आसान और सस्ती बनाते हैं।
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("मुख्य विशेषताएं", heading_style))
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=10, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("विवरण", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("ऑन-रोड मूल्य का 100% तक (शर्तें लागू)<br/>नई कार: Rs. 1 लाख - Rs. 1 करोड़<br/>पुरानी कार: Rs. 50,000 - Rs. 50 लाख<br/>दोपहिया: Rs. 30,000 - Rs. 3 लाख", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("नई कार: 8.50% - 10.50% प्रति वर्ष<br/>पुरानी कार: 10.50% - 13.50% प्रति वर्ष<br/>दोपहिया: 11.00% - 14.00% प्रति वर्ष", table_cell_style)],
        [Paragraph("लोन-टू-वैल्यू (LTV)", table_cell_style), Paragraph("नए वाहन: 90% तक<br/>पुराने वाहन: 80% तक<br/>दोपहिया: 95% तक", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("नई कार: 7 वर्ष तक (84 महीने)<br/>पुरानी कार: 5 वर्ष तक (60 महीने)<br/>दोपहिया: 5 वर्ष तक (60 महीने)", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("नई: लोन राशि का 1% + GST<br/>पुरानी: लोन राशि का 1.5% + GST", table_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", table_cell_style), Paragraph("12 महीने के बाद शून्य<br/>12 महीने के भीतर पूर्व भुगतान करने पर 3% + GST", table_cell_style)],
        [Paragraph("बीमा", table_cell_style), Paragraph("व्यापक बीमा अनिवार्य<br/>जीरो डिप्रिसिएशन कवर अनुशंसित", table_cell_style)],
        [Paragraph("अनुमोदन समय", table_cell_style), Paragraph("तत्काल सिद्धांत अनुमोदन के साथ 24-48 घंटे", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Vehicle Types Covered
    story.append(Paragraph("कवर किए गए वाहनों के प्रकार", heading_style))
    vehicle_types = [
        "<b>1. नई कारें:</b> सभी ब्रांडों के अधिकृत डीलरों से यात्री कारें - मारुति, हुंडई, टाटा, महिंद्रा, टोयोटा, होंडा, आदि।",
        "<b>2. पुरानी कारें:</b> लोन बंद होने के समय 8 वर्ष तक पुरानी कारें। वाहन आयु + लोन अवधि ≤ 10 वर्ष।",
        "<b>3. दोपहिया:</b> सभी प्रमुख ब्रांडों से नई और पुरानी मोटरसाइकिल, स्कूटर - होंडा, हीरो, बजाज, TVS, रॉयल एनफील्ड, आदि।",
        "<b>4. वाणिज्यिक वाहन:</b> हल्के वाणिज्यिक वाहन, माल वाहक, टैक्सी (अलग योजना - पात्रता जांचें)।",
        "<b>5. इलेक्ट्रिक वाहन:</b> सब्सिडी लाभ के साथ EV के लिए विशेष दरें (नई EV कारों पर 0.25% दर छूट)।",
    ]
    
    for vtype in vehicle_types:
        story.append(Paragraph(vtype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("वेतनभोगी", eligibility_header_style), Paragraph("स्व-नियोजित", eligibility_header_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("21 - 65 वर्ष", eligibility_cell_style), Paragraph("25 - 70 वर्ष", eligibility_cell_style)],
        [Paragraph("न्यूनतम आय", eligibility_cell_style), Paragraph("Rs. 20,000 प्रति माह (मेट्रो)<br/>Rs. 15,000 प्रति माह (गैर-मेट्रो)", eligibility_cell_style), Paragraph("Rs. 3,00,000 प्रति वर्ष (ITR)", eligibility_cell_style)],
        [Paragraph("काम का अनुभव", eligibility_cell_style), Paragraph("न्यूनतम 1 वर्ष कुल<br/>(वर्तमान नियोक्ता में 6 महीने)", eligibility_cell_style), Paragraph("व्यवसाय में न्यूनतम 2 वर्ष", eligibility_cell_style)],
        [Paragraph("क्रेडिट स्कोर", eligibility_cell_style), Paragraph("सर्वोत्तम दरों के लिए न्यूनतम 700<br/>650-699: उच्च दर<br/>650 से नीचे: मामला-दर-मामला", eligibility_cell_style), Paragraph("सर्वोत्तम दरों के लिए न्यूनतम 700<br/>650-699: उच्च दर<br/>650 से नीचे: मामला-दर-मामला", eligibility_cell_style)],
        [Paragraph("डाउन पेमेंट", eligibility_cell_style), Paragraph("नई के लिए न्यूनतम 10%<br/>पुराने वाहनों के लिए 20%", eligibility_cell_style), Paragraph("नई के लिए न्यूनतम 15%<br/>पुराने वाहनों के लिए 25%", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    
    story.append(PageBreak())
    
    # Documents Required
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    story.append(Paragraph("वेतनभोगी व्यक्तियों के लिए:", subheading_style))
    salaried_docs = [
        "• पहचान प्रमाण: आधार कार्ड, PAN कार्ड (अनिवार्य)",
        "• पता प्रमाण: आधार, पासपोर्ट, उपयोगिता बिल",
        "• आय प्रमाण: पिछले 3 महीने के वेतन स्लिप",
        "• बैंक स्टेटमेंट: वेतन क्रेडिट दिखाने वाला पिछले 6 महीने का स्टेटमेंट",
        "• वाहन दस्तावेज: डीलर से प्रोफॉर्मा इनवॉइस, वाहन कोटेशन",
        "• फोटो: 2 पासपोर्ट साइज फोटो",
        "• पुराने वाहनों के लिए: मूल RC, बीमा पॉलिसी, पिछले मालिक का NOC, मूल्यांकन रिपोर्ट",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("स्व-नियोजित के लिए:", subheading_style))
    self_emp_docs = [
        "• पहचान और पता: आधार, PAN (अनिवार्य)",
        "• व्यवसाय प्रमाण: GST पंजीकरण, दुकान लाइसेंस, व्यवसाय पंजीकरण",
        "• आय प्रमाण: आय गणना के साथ पिछले 2 वर्षों के ITR, लेखा परीक्षित वित्तीय",
        "• बैंक स्टेटमेंट: पिछले 12 महीने का व्यवसाय खाता स्टेटमेंट",
        "• वाहन दस्तावेज: प्रोफॉर्मा इनवॉइस, कोटेशन",
        "• पुराने के लिए: RC कॉपी, बीमा, NOC, वाहन मूल्यांकन रिपोर्ट",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI गणना उदाहरण", heading_style))
    emi_header_style = ParagraphStyle('EMIHeader', parent=styles['Normal'],
                                     fontSize=7, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_CENTER)
    emi_cell_style = ParagraphStyle('EMICell', parent=styles['Normal'],
                                   fontSize=7, fontName=HINDI_FONT,
                                   alignment=TA_CENTER)
    
    emi_data = [
        [Paragraph("वाहन प्रकार", emi_header_style), Paragraph("लोन राशि", emi_header_style), Paragraph("दर", emi_header_style), Paragraph("अवधि", emi_header_style), Paragraph("मासिक EMI", emi_header_style), Paragraph("कुल ब्याज", emi_header_style)],
        [Paragraph("नई कार\n(हैचबैक)", emi_cell_style), Paragraph("Rs. 5,00,000", emi_cell_style), Paragraph("9.00%", emi_cell_style), Paragraph("5 वर्ष", emi_cell_style), Paragraph("Rs. 10,378", emi_cell_style), Paragraph("Rs. 1,22,680", emi_cell_style)],
        [Paragraph("नई कार\n(सेडान)", emi_cell_style), Paragraph("Rs. 10,00,000", emi_cell_style), Paragraph("8.75%", emi_cell_style), Paragraph("7 वर्ष", emi_cell_style), Paragraph("Rs. 15,071", emi_cell_style), Paragraph("Rs. 2,65,972", emi_cell_style)],
        [Paragraph("पुरानी कार\n(5 वर्ष पुरानी)", emi_cell_style), Paragraph("Rs. 3,00,000", emi_cell_style), Paragraph("11.50%", emi_cell_style), Paragraph("4 वर्ष", emi_cell_style), Paragraph("Rs. 7,822", emi_cell_style), Paragraph("Rs. 75,456", emi_cell_style)],
        [Paragraph("दोपहिया\n(नई)", emi_cell_style), Paragraph("Rs. 1,00,000", emi_cell_style), Paragraph("12.00%", emi_cell_style), Paragraph("3 वर्ष", emi_cell_style), Paragraph("Rs. 3,321", emi_cell_style), Paragraph("Rs. 19,556", emi_cell_style)],
        [Paragraph("इलेक्ट्रिक कार\n(नई - विशेष)", emi_cell_style), Paragraph("Rs. 8,00,000", emi_cell_style), Paragraph("8.25%", emi_cell_style), Paragraph("5 वर्ष", emi_cell_style), Paragraph("Rs. 16,258", emi_cell_style), Paragraph("Rs. 1,75,480", emi_cell_style)],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 0.8*inch, 1*inch, 1*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Fees and Charges
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("नई: लोन राशि का 1% + GST<br/>पुरानी: लोन राशि का 1.5% + GST<br/>दोपहिया: 1% + GST", fees_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", fees_cell_style), Paragraph("12 EMI भुगतान के बाद शून्य<br/>12 महीने के भीतर बकाया का 3% + GST", fees_cell_style)],
        [Paragraph("फोरक्लोजर शुल्क", fees_cell_style), Paragraph("18 EMI भुगतान के बाद शून्य<br/>18 महीने के भीतर बकाया का 4% + GST", fees_cell_style)],
        [Paragraph("देर से भुगतान शुल्क", fees_cell_style), Paragraph("बकाया पर प्रति माह 2% या Rs. 500 (जो भी अधिक हो)", fees_cell_style)],
        [Paragraph("NACH/चेक बाउंस", fees_cell_style), Paragraph("प्रति बाउंस Rs. 500", fees_cell_style)],
        [Paragraph("डुप्लिकेट दस्तावेज", fees_cell_style), Paragraph("प्रति दस्तावेज Rs. 250 + GST", fees_cell_style)],
        [Paragraph("RC ट्रांसफर सहायता", fees_cell_style), Paragraph("Rs. 1,000 + GST (वैकल्पिक सेवा)", fees_cell_style)],
        [Paragraph("बीमा प्रसंस्करण", fees_cell_style), Paragraph("बैंक के माध्यम से पॉलिसियों के लिए मुफ्त<br/>बाहरी बीमा के लिए Rs. 500 + GST", fees_cell_style)],
        [Paragraph("वाहन मूल्यांकन", fees_cell_style), Paragraph("Rs. 500 से Rs. 2,000 (वाहन मूल्य के आधार पर) - पुराने वाहनों के लिए", fees_cell_style)],
        [Paragraph("लोन रद्दीकरण", fees_cell_style), Paragraph("Rs. 2,000 + GST (अनुमोदन के बाद, भुगतान से पहले)", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[2.5*inch, 4*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    # Insurance Requirements
    story.append(Paragraph("बीमा आवश्यकताएं", heading_style))
    insurance_info = [
        "• <b>व्यापक बीमा अनिवार्य:</b> मोटर वाहन अधिनियम के अनुसार स्वयं की क्षति + तृतीय-पक्ष दायित्व को कवर करना चाहिए।",
        "• <b>बैंक को-लाभार्थी के रूप में:</b> बीमा पॉलिसी में सन नेशनल बैंक को को-लाभार्थी/हाइपोथेकेशन के रूप में जोड़ा जाना चाहिए।",
        "• <b>जीरो डिप्रिसिएशन कवर:</b> नए वाहनों के लिए अत्यधिक अनुशंसित (पहले 5 वर्ष)।",
        "• <b>रिटर्न टू इनवॉइस (RTI):</b> कुल नुकसान के मामले में पूर्ण वाहन मूल्य सुरक्षा के लिए वैकल्पिक ऐड-ऑन।",
        "• <b>नवीकरण अनिवार्य:</b> बीमा लगातार नवीकृत होना चाहिए। गैर-नवीकरण जुर्माना और लोन वापसी को आकर्षित करता है।",
        "• <b>इंजन सुरक्षा:</b> कारों के लिए अनुशंसित ऐड-ऑन (पानी के प्रवेश के कारण इंजन क्षति को कवर करता है)।",
        "• <b>EMI सुरक्षा बीमा:</b> दुर्भाग्यपूर्ण घटनाओं के मामले में परिवार को EMI बोझ से बचाने के लिए वैकल्पिक कवर।",
    ]
    
    for info in insurance_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: मुझे अधिकतम कितनी लोन राशि मिल सकती है?</b>",
         "नए वाहनों के लिए ऑन-रोड मूल्य का 90% तक (10% डाउन पेमेंट आवश्यक)। पुराने वाहनों के लिए, 80% तक। वास्तविक राशि आपकी आय, क्रेडिट स्कोर और चुकौती क्षमता पर निर्भर करती है।"),
        
        ("<b>Q2: क्या मैं एक व्यक्तिगत विक्रेता से पुरानी कार खरीद सकता हूं?</b>",
         "हां, हम व्यक्तियों, डीलरों या ऑनलाइन प्लेटफॉर्म से खरीदी गई कारों के लिए लोन प्रदान करते हैं। वाहन आपके शहर/राज्य में पंजीकृत होना चाहिए और निर्दिष्ट सीमाओं से अधिक पुराना नहीं होना चाहिए।"),
        
        ("<b>Q3: क्या हाइपोथेकेशन अनिवार्य है? यह कब हटाया जाता है?</b>",
         "हां, बैंक पूर्ण चुकौती तक वाहन पर हाइपोथेकेशन रखता है। लोन बंद होने के बाद, हम RC से हाइपोथेकेशन हटाने के लिए 7 कार्य दिवसों के भीतर NOC प्रदान करते हैं।"),
        
        ("<b>Q4: यदि मैं लोन बंद होने से पहले वाहन बेचना चाहूं तो क्या होगा?</b>",
         "आपको पहले लोन बंद करना होगा या खरीदार को लोन ट्रांसफर लेने के लिए कहना होगा। हम फोरक्लोजर कोटेशन प्रदान करते हैं। खरीदार हमसे लोन भी ले सकता है (बैलेंस ट्रांसफर योजना)।"),
        
        ("<b>Q5: क्या इलेक्ट्रिक वाहनों के लिए विशेष दरें हैं?</b>",
         "हां, नए इलेक्ट्रिक वाहनों के लिए ब्याज दर पर 0.25% छूट। यह FAME II योजना के तहत उपलब्ध सरकारी सब्सिडी के अतिरिक्त है।"),
        
        ("<b>Q6: क्या मैं दूसरे बैंक से अपना मौजूदा ऑटो लोन स्थानांतरित कर सकता हूं?</b>",
         "हां, बैलेंस ट्रांसफर स्वीकार किया जाता है यदि आपने कम से कम 12 EMI का भुगतान किया है। दर लाभ उपलब्ध हैं। प्रोसेसिंग शुल्क 1% + GST।"),
        
        ("<b>Q7: यदि मैं वित्तीय कठिनाई के कारण EMI भुगतान चूक जाऊं तो क्या होगा?</b>",
         "तुरंत हमसे संपर्क करें। हम आपकी स्थिति के आधार पर आपके लोन को पुनर्गठित कर सकते हैं, अवधि बढ़ा सकते हैं, या मोरेटोरियम प्रदान कर सकते हैं। EMI को नजरअंदाज करने से जुर्माना और पुनर्प्राप्ति होती है।"),
        
        ("<b>Q8: क्या लोन बीमा अनिवार्य है?</b>",
         "वाहन बीमा कानून और बैंक आवश्यकता द्वारा अनिवार्य है। EMI सुरक्षा बीमा वैकल्पिक है लेकिन परिवार की वित्तीय सुरक्षा के लिए अनुशंसित है।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Important Terms
    story.append(Paragraph("महत्वपूर्ण नियम और शर्तें", heading_style))
    terms = [
        "• वाहन लोन आवेदक/सह-आवेदक के नाम पर ही पंजीकृत होना चाहिए।",
        "• लोन बंद होने तक सन नेशनल बैंक के पक्ष में हाइपोथेकेशन अनिवार्य है।",
        "• बैंक को को-लाभार्थी के रूप में व्यापक बीमा पूरे लोन अवधि के दौरान अनिवार्य है।",
        "• EMI भुगतान के लिए PDC (पोस्ट-डेटेड चेक) या NACH मैंडेट अनिवार्य है।",
        "• लोन बंद होने तक वाहन को बेचा, स्थानांतरित या किसी अन्य पक्ष को हाइपोथेकेट नहीं किया जा सकता है।",
        "• पुराने वाहनों के लिए: तकनीकी और कानूनी सत्यापन अनिवार्य। वाहन आयु + लोन अवधि ≤ 10 वर्ष।",
        "• ब्याज दर पूरी अवधि के लिए निश्चित है। प्रोसेसिंग शुल्क गैर-वापसी योग्य है।",
        "• 3 लगातार EMI में डिफॉल्ट बैंक को SARFAESI अधिनियम के अनुसार वाहन को पुनर्प्राप्त करने का अधिकार देता है।",
        "• RTO पंजीकरण, सड़क कर और अन्य शुल्क ग्राहक की जिम्मेदारी है।",
        "• बैंक निर्दिष्ट आयु सीमाओं से अधिक पुराने वाहनों के लिए लोन प्रदान नहीं करता है।",
        "• वाणिज्यिक वाहन लोन अलग शर्तों के अधीन हैं - विवरण के लिए शाखा से संपर्क करें।",
    ]
    
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>ऑटो लोन सहायता के लिए</b><br/>
    कस्टमर केयर: 1800-123-4567 | 080-1234-5678<br/>
    ईमेल: autoloans@sunnationalbank.in<br/>
    वेबसाइट: www.sunnationalbank.in/auto-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>अधिकृत डीलर पर जाएं या ऑनलाइन आवेदन करें - तत्काल सिद्धांत अनुमोदन!</i>
    </para>
    """
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "ऑटो लोन गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "ऑटो लोन गाइड"))
    return output_path


def create_education_loan_doc():
    """Create comprehensive Education Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "education_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("एजुकेशन लोन", title_style))
    story.append(Paragraph("अपने भविष्य में निवेश करें - भारत या विदेश में अध्ययन करें", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """
    सन नेशनल बैंक एजुकेशन लोन छात्रों को भारत या विदेश में उच्च शिक्षा प्राप्त करने में मदद करता है। 
    हम ट्यूशन फीस, छात्रावास खर्च, किताबें, उपकरण, यात्रा और अन्य शिक्षा-संबंधी लागतों को कवर करते हैं। 
    लचीले चुकौती, मोरेटोरियम अवधि और Section 80E के तहत कर लाभों के साथ, हम सभी योग्य छात्रों के लिए गुणवत्तापूर्ण शिक्षा को सुलभ बनाते हैं।
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("मुख्य विशेषताएं", heading_style))
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=9, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=8, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("घरेलू शिक्षा", table_header_style), Paragraph("अंतर्राष्ट्रीय शिक्षा", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("Rs. 10 लाख तक (कोई गारंटी नहीं)<br/>Rs. 10-20 लाख (गारंटी के साथ)", table_cell_style), Paragraph("Rs. 1.5 करोड़ तक<br/>(Rs. 7.5 लाख से अधिक पर गारंटी अनिवार्य)", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("8.50% - 11.50% प्रति वर्ष", table_cell_style), Paragraph("9.50% - 12.50% प्रति वर्ष", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("15 वर्ष तक", table_cell_style), Paragraph("15 वर्ष तक", table_cell_style)],
        [Paragraph("मोरेटोरियम अवधि", table_cell_style), Paragraph("पाठ्यक्रम अवधि + 1 वर्ष<br/>या नौकरी मिलने के 6 महीने बाद (जो भी पहले हो)", table_cell_style), Paragraph("पाठ्यक्रम अवधि + 1 वर्ष<br/>या नौकरी मिलने के 6 महीने बाद (जो भी पहले हो)", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("Rs. 4 लाख तक के लोन के लिए शून्य<br/>Rs. 4 लाख से अधिक पर 1% + GST", table_cell_style), Paragraph("लोन राशि का 1% + GST", table_cell_style)],
        [Paragraph("मार्जिन मनी", table_cell_style), Paragraph("5% (Rs. 4 लाख तक)<br/>15% (Rs. 4 लाख से अधिक)", table_cell_style), Paragraph("सभी लोन राशियों के लिए 15%", table_cell_style)],
        [Paragraph("कर लाभ", table_cell_style), Paragraph("8 वर्षों के लिए Section 80E के तहत भुगतान किया गया ब्याज कटौती योग्य", table_cell_style), Paragraph("8 वर्षों के लिए Section 80E के तहत भुगतान किया गया ब्याज कटौती योग्य", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Courses Covered
    story.append(Paragraph("कवर किए गए पाठ्यक्रम और संस्थान", heading_style))
    courses_info = [
        "<b>स्नातक पाठ्यक्रम:</b> इंजीनियरिंग (B.Tech/B.E.), मेडिकल (MBBS), प्रबंधन (BBA), कॉमर्स (B.Com), विज्ञान, कला, डिप्लोमा पाठ्यक्रम।",
        "<b>स्नातकोत्तर:</b> M.Tech, MBA, MS, MCA, M.Com, M.Sc., मेडिकल PG (MD/MS), CA, CFA, आदि।",
        "<b>पेशेवर पाठ्यक्रम:</b> चार्टर्ड अकाउंटेंसी, कंपनी सेक्रेटरी, CFA, एक्चुअरियल साइंस, आदि।",
        "<b>प्रतियोगी परीक्षा कोचिंग:</b> IIT-JEE, NEET, UPSC, CAT, GRE, GMAT, IELTS तैयारी पाठ्यक्रम (Rs. 2 लाख तक)।",
        "<b>विदेशी शिक्षा:</b> USA, UK, कनाडा, ऑस्ट्रेलिया, जर्मनी, सिंगापुर, आदि में स्नातक और स्नातकोत्तर पाठ्यक्रम।",
    ]
    
    for course in courses_info:
        story.append(Paragraph(course, bullet_style))
    
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("<b>अनुमोदित संस्थान:</b>", subheading_style))
    inst_info = [
        "• सभी IITs, NITs, IIMs, AIIMS और अन्य केंद्रीय/राज्य सरकारी संस्थान",
        "• भारत में UGC/AICTE/MCI/PCI अनुमोदित कॉलेज और विश्वविद्यालय",
        "• अनुमोदित सूची में सूचीबद्ध विदेशी विश्वविद्यालय (शाखा से जांचें)",
        "• पेशेवर संस्थान जैसे ICAI, ICSI, ICWAI, एक्चुअरियल सोसाइटी",
    ]
    for inst in inst_info:
        story.append(Paragraph(inst, bullet_style))
    
    story.append(PageBreak())
    
    # Expenses Covered
    story.append(Paragraph("लोन के तहत कवर किए गए खर्च", heading_style))
    expenses_header_style = ParagraphStyle('ExpensesHeader', parent=styles['Normal'],
                                         fontSize=9, fontName=HINDI_FONT_BOLD,
                                         textColor=colors.whitesmoke, alignment=TA_LEFT)
    expenses_cell_style = ParagraphStyle('ExpensesCell', parent=styles['Normal'],
                                       fontSize=8, fontName=HINDI_FONT,
                                       alignment=TA_LEFT)
    
    expenses = [
        [Paragraph("खर्च श्रेणी", expenses_header_style), Paragraph("कवरेज विवरण", expenses_header_style)],
        [Paragraph("ट्यूशन फीस", expenses_cell_style), Paragraph("संस्थान द्वारा लगाई गई पूर्ण ट्यूशन और विकास शुल्क", expenses_cell_style)],
        [Paragraph("छात्रावास/आवास", expenses_cell_style), Paragraph("छात्रावास शुल्क या ऑफ-कैंपस आवास के लिए किराया (किराया समझौते के साथ)", expenses_cell_style)],
        [Paragraph("किताबें और उपकरण", expenses_cell_style), Paragraph("पाठ्यपुस्तकों की लागत, पुस्तकालय शुल्क, अध्ययन सामग्री, लैपटॉप/उपकरण (बिल के साथ)", expenses_cell_style)],
        [Paragraph("परीक्षा शुल्क", expenses_cell_style), Paragraph("सेमेस्टर/वार्षिक परीक्षा शुल्क, परियोजना शुल्क, थीसिस जमा शुल्क", expenses_cell_style)],
        [Paragraph("यात्रा खर्च", expenses_cell_style), Paragraph("विदेशी शिक्षा के लिए: हवाई किराया (इकोनॉमी क्लास)<br/>घरेलू के लिए: आवश्यक होने पर यात्रा (सीमित)", expenses_cell_style)],
        [Paragraph("अध्ययन यात्रा/परियोजना", expenses_cell_style), Paragraph("शैक्षिक यात्राएं, इंटर्नशिप परियोजना लागत (यदि पाठ्यक्रम का हिस्सा है)", expenses_cell_style)],
        [Paragraph("सावधानी जमा", expenses_cell_style), Paragraph("कॉलेज को वापसी योग्य जमा (बैंक को वापस किया जाना है)", expenses_cell_style)],
        [Paragraph("भवन निधि", expenses_cell_style), Paragraph("यदि लागू हो तो एक बार का भवन/विकास शुल्क", expenses_cell_style)],
        [Paragraph("बीमा प्रीमियम", expenses_cell_style), Paragraph("अनिवार्य छात्र बीमा, विदेश में स्वास्थ्य बीमा", expenses_cell_style)],
        [Paragraph("रहने की लागत", expenses_cell_style), Paragraph("विदेश के लिए: मानदंड के अनुसार रहने का खर्च (देश के अनुसार भिन्न)", expenses_cell_style)],
    ]
    
    expenses_table = Table(expenses, colWidths=[2*inch, 4.5*inch])
    expenses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(expenses_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("छात्र", eligibility_header_style), Paragraph("सह-आवेदक (माता-पिता/अभिभावक)", eligibility_header_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("18 वर्ष और उससे अधिक<br/>(लोन के समय)", eligibility_cell_style), Paragraph("21 - 65 वर्ष", eligibility_cell_style)],
        [Paragraph("शैक्षणिक रिकॉर्ड", eligibility_cell_style), Paragraph("अनुमोदित संस्थान में प्रवेश पुष्टि<br/>अच्छा शैक्षणिक रिकॉर्ड (योग्यता परीक्षा में 60%+)", eligibility_cell_style), Paragraph("लागू नहीं", eligibility_cell_style)],
        [Paragraph("सह-उधारकर्ता", eligibility_cell_style), Paragraph("अनिवार्य आवश्यकता<br/>(माता-पिता/अभिभावक/पति/पत्नी)", eligibility_cell_style), Paragraph("आय प्रमाण अनिवार्य<br/>अच्छा क्रेडिट स्कोर आवश्यक", eligibility_cell_style)],
        [Paragraph("आय आवश्यकता", eligibility_cell_style), Paragraph("छात्र के लिए लागू नहीं", eligibility_cell_style), Paragraph("घरेलू के लिए न्यूनतम Rs. 2 लाख प्रति वर्ष<br/>अंतर्राष्ट्रीय के लिए Rs. 3 लाख प्रति वर्ष", eligibility_cell_style)],
        [Paragraph("क्रेडिट स्कोर", eligibility_cell_style), Paragraph("लागू नहीं<br/>(छात्र का क्रेडिट इतिहास नहीं हो सकता है)", eligibility_cell_style), Paragraph("न्यूनतम 650 (700+ पसंदीदा)", eligibility_cell_style)],
        [Paragraph("राष्ट्रीयता", eligibility_cell_style), Paragraph("भारतीय नागरिक", eligibility_cell_style), Paragraph("भारतीय नागरिक या NRI माता-पिता", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Documents Required
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    story.append(Paragraph("छात्र दस्तावेज:", subheading_style))
    student_docs = [
        "• पहचान प्रमाण: आधार कार्ड, PAN कार्ड, पासपोर्ट (विदेशी शिक्षा के लिए)",
        "• प्रवेश प्रमाण: संस्थान से प्रवेश पत्र/ऑफर लेटर (बिना शर्त होना चाहिए)",
        "• शैक्षणिक रिकॉर्ड: 10वीं, 12वीं, स्नातक अंक पत्र और प्रमाणपत्र",
        "• प्रवेश परीक्षा स्कोरकार्ड: JEE, NEET, CAT, GRE, GMAT, IELTS, आदि (यदि लागू हो)",
        "• फीस संरचना: पूरे पाठ्यक्रम अवधि के लिए संस्थान से आधिकारिक फीस अनुसूची",
        "• छात्रवृत्ति पत्र: यदि कोई छात्रवृत्ति स्वीकृत है, तो अनुमोदन पत्र प्रदान करें",
        "• पासपोर्ट: अंतर्राष्ट्रीय शिक्षा के लिए (अनिवार्य)",
        "• वीजा दस्तावेज: I-20 (USA), CAS (UK), COE (ऑस्ट्रेलिया), आदि जैसा लागू हो",
    ]
    for doc_item in student_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("सह-आवेदक (माता-पिता/अभिभावक) दस्तावेज:", subheading_style))
    parent_docs = [
        "• पहचान और पता: आधार, PAN कार्ड (दोनों अनिवार्य)",
        "• आय प्रमाण: पिछले 6 महीने के वेतन स्लिप (वेतनभोगी) या पिछले 2 वर्षों के ITR (स्व-नियोजित)",
        "• बैंक स्टेटमेंट: वेतनभोगी के लिए पिछले 6 महीने, स्व-नियोजित के लिए 12 महीने",
        "• रोजगार प्रमाण: रोजगार प्रमाणपत्र, नियुक्ति पत्र",
        "• प्रॉपर्टी दस्तावेज: यदि गारंटी दे रहे हैं (प्रॉपर्टी कागज, मूल्यांकन रिपोर्ट)",
        "• संबंध प्रमाण: जन्म प्रमाणपत्र, आधार, या छात्र के साथ संबंध दिखाने वाला कोई दस्तावेज",
    ]
    for doc_item in parent_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # Repayment Structure
    story.append(Paragraph("चुकौती संरचना और मोरेटोरियम", heading_style))
    repayment_info = """
    एजुकेशन लोन चुकौती मोरेटोरियम अवधि और लचीले विकल्पों के साथ छात्र-अनुकूल बनाई गई है:
    """
    story.append(Paragraph(repayment_info, normal_style))
    
    repay_phases = [
        ("<b>चरण 1 - अध्ययन अवधि (पाठ्यक्रम अवधि):</b>",
         "इस चरण के दौरान, EMI भुगतान की आवश्यकता नहीं है। हालांकि, आप कुल ब्याज बोझ को कम करने के लिए केवल ब्याज EMI का भुगतान करना चुन सकते हैं (वैकल्पिक)।"),
        
        ("<b>चरण 2 - मोरेटोरियम अवधि:</b>",
         "पाठ्यक्रम पूरा होने के बाद, आपको पाठ्यक्रम अवधि + 1 वर्ष या नौकरी मिलने के 6 महीने बाद मोरेटोरियम मिलता है (जो भी पहले हो)। " 
         "इस अवधि के दौरान, कोई EMI भुगतान आवश्यक नहीं है, लेकिन ब्याज मूलधन में जोड़ा जाता है (चक्रवृद्धि)।"),
        
        ("<b>चरण 3 - चुकौती अवधि:</b>",
         "मोरेटोरियम समाप्त होने के बाद नियमित EMI शुरू होती है। अवधि 15 वर्ष तक हो सकती है। आप मासिक, त्रैमासिक, या बुलेट चुकौती विकल्प चुन सकते हैं।"),
    ]
    
    for phase_title, phase_desc in repay_phases:
        story.append(Paragraph(phase_title, subheading_style))
        story.append(Paragraph(phase_desc, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>विशेष विकल्प:</b>", subheading_style))
    special_options = [
        "• <b>अध्ययन के दौरान साधारण ब्याज:</b> कुल ब्याज बचाने के लिए अध्ययन के दौरान केवल ब्याज EMI का भुगतान करने का विकल्प",
        "• <b>आंशिक भुगतान:</b> मूलधन को कम करने के लिए कभी भी बिना शुल्क के एकमुश्त पूर्व भुगतान करें",
        "• <b>Step-up EMI:</b> कम EMI से शुरू करें और आय बढ़ने पर वार्षिक रूप से बढ़ाएं",
        "• <b>लचीली अवधि:</b> आराम के आधार पर 5 से 15 वर्ष तक चुकौती अवधि चुनें",
    ]
    for option in special_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI गणना उदाहरण", heading_style))
    story.append(Paragraph("(मान लें कि मोरेटोरियम ब्याज को पूंजीकृत किया जाता है और EMI पाठ्यक्रम पूरा होने + 1 वर्ष के बाद शुरू होती है)", normal_style))
    
    emi_header_style = ParagraphStyle('EMIHeader', parent=styles['Normal'],
                                     fontSize=7, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_CENTER)
    emi_cell_style = ParagraphStyle('EMICell', parent=styles['Normal'],
                                   fontSize=7, fontName=HINDI_FONT,
                                   alignment=TA_CENTER)
    
    emi_data = [
        [Paragraph("पाठ्यक्रम", emi_header_style), Paragraph("कुल लोन", emi_header_style), Paragraph("दर", emi_header_style), Paragraph("पाठ्यक्रम+मोरेटोरियम", emi_header_style), Paragraph("चुकौती अवधि", emi_header_style), Paragraph("मासिक EMI", emi_header_style)],
        [Paragraph("B.Tech (भारत)", emi_cell_style), Paragraph("Rs. 8,00,000", emi_cell_style), Paragraph("9.00%", emi_cell_style), Paragraph("4+1 = 5 वर्ष", emi_cell_style), Paragraph("10 वर्ष", emi_cell_style), Paragraph("Rs. 13,927", emi_cell_style)],
        [Paragraph("MBA (भारत)", emi_cell_style), Paragraph("Rs. 15,00,000", emi_cell_style), Paragraph("9.50%", emi_cell_style), Paragraph("2+1 = 3 वर्ष", emi_cell_style), Paragraph("10 वर्ष", emi_cell_style), Paragraph("Rs. 26,199", emi_cell_style)],
        [Paragraph("MS (USA)", emi_cell_style), Paragraph("Rs. 50,00,000", emi_cell_style), Paragraph("10.50%", emi_cell_style), Paragraph("2+1 = 3 वर्ष", emi_cell_style), Paragraph("15 वर्ष", emi_cell_style), Paragraph("Rs. 71,955", emi_cell_style)],
        [Paragraph("MBBS (भारत)", emi_cell_style), Paragraph("Rs. 25,00,000", emi_cell_style), Paragraph("8.75%", emi_cell_style), Paragraph("5.5+1 = 6.5 वर्ष", emi_cell_style), Paragraph("15 वर्ष", emi_cell_style), Paragraph("Rs. 43,462", emi_cell_style)],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 1.1*inch, 1*inch, 1*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Tax Benefits
    story.append(Paragraph("आयकर लाभ (Section 80E)", heading_style))
    tax_info = [
        "• <b>ब्याज पर कटौती:</b> एजुकेशन लोन पर भुगतान किया गया ब्याज Section 80E के तहत कर योग्य आय से पूरी तरह कटौती योग्य है।",
        "• <b>अवधि:</b> पहले EMI भुगतान के वर्ष से शुरू होकर अधिकतम 8 वर्षों के लिए लाभ उपलब्ध है।",
        "• <b>कोई ऊपरी सीमा नहीं:</b> कटौती राशि पर कोई अधिकतम सीमा नहीं है - भुगतान किया गया पूरा ब्याज कटौती योग्य है।",
        "• <b>कौन दावा कर सकता है:</b> लोन व्यक्ति (माता-पिता/छात्र) द्वारा लिया जाना चाहिए। HUF या कंपनियां दावा नहीं कर सकती हैं।",
        "• <b>पाठ्यक्रम आवश्यकता:</b> लोन उच्च शिक्षा (12वीं कक्षा के बाद) के लिए होना चाहिए स्वयं, पति/पत्नी, या बच्चों के लिए।",
        "• <b>ऋणदाता आवश्यकता:</b> लोन बैंक, वित्तीय संस्थान, या अनुमोदित चैरिटी से होना चाहिए। रिश्तेदारों से नहीं।",
        "• <b>प्रमाणपत्र आवश्यक:</b> बैंक IT रिटर्न दाखिल करने के लिए वार्षिक रूप से ब्याज प्रमाणपत्र प्रदान करेगा।",
    ]
    
    for tax_point in tax_info:
        story.append(Paragraph(tax_point, bullet_style))
    
    story.append(Spacer(1, 0.15*inch))
    tax_example = """
    <b>उदाहरण:</b> यदि आपने एक वर्ष में Rs. 1,50,000 ब्याज का भुगतान किया है और आप 30% कर स्लैब में हैं, 
    तो आप कर में Rs. 45,000 बचाते हैं (Rs. 1,50,000 × 30% = Rs. 45,000)। यह लाभ 8 लगातार निर्धारण वर्षों के लिए उपलब्ध है।
    """
    story.append(Paragraph(tax_example, normal_style))
    
    story.append(PageBreak())
    
    # Fees and Charges
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("घरेलू", fees_header_style), Paragraph("अंतर्राष्ट्रीय", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("शून्य (Rs. 4 लाख तक)<br/>Rs. 4 लाख से अधिक पर 1% + GST", fees_cell_style), Paragraph("लोन राशि का 1% + GST", fees_cell_style)],
        [Paragraph("पूर्व भुगतान/फोरक्लोजर", fees_cell_style), Paragraph("शून्य - कभी भी पूर्व भुगतान के लिए कोई शुल्क नहीं", fees_cell_style), Paragraph("शून्य - कभी भी पूर्व भुगतान के लिए कोई शुल्क नहीं", fees_cell_style)],
        [Paragraph("देर से भुगतान शुल्क", fees_cell_style), Paragraph("बकाया राशि पर Rs. 500 या प्रति माह 2% (जो भी अधिक हो)", fees_cell_style), Paragraph("बकाया राशि पर Rs. 500 या प्रति माह 2% (जो भी अधिक हो)", fees_cell_style)],
        [Paragraph("चेक/NACH बाउंस", fees_cell_style), Paragraph("प्रति बाउंस Rs. 500", fees_cell_style), Paragraph("प्रति बाउंस Rs. 500", fees_cell_style)],
        [Paragraph("लोन पुनर्गठन शुल्क", fees_cell_style), Paragraph("Rs. 1,000 + GST (यदि अवधि संशोधित की गई है)", fees_cell_style), Paragraph("Rs. 1,000 + GST (यदि अवधि संशोधित की गई है)", fees_cell_style)],
        [Paragraph("डुप्लिकेट प्रमाणपत्र", fees_cell_style), Paragraph("Rs. 250 + GST", fees_cell_style), Paragraph("Rs. 250 + GST", fees_cell_style)],
        [Paragraph("गारंटी मूल्यांकन", fees_cell_style), Paragraph("वास्तविक के अनुसार (Rs. 500 से Rs. 3,000)", fees_cell_style), Paragraph("वास्तविक के अनुसार (Rs. 2,000 से Rs. 5,000)", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[2.2*inch, 2.2*inch, 2.1*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: क्या मैं बिना गारंटी के लोन प्राप्त कर सकता हूं?</b>",
         "हां, Rs. 7.5 लाख तक के लोन के लिए, कोई गारंटी आवश्यक नहीं है। तृतीय-पक्ष गारंटी की आवश्यकता हो सकती है। Rs. 7.5 लाख से अधिक पर, गारंटी (प्रॉपर्टी/FD/LIC) अनिवार्य है।"),
        
        ("<b>Q2: यदि मुझे प्रवेश नहीं मिलता है तो क्या होगा? क्या शुल्क वापस किया जाएगा?</b>",
         "हां, यदि प्रवेश पुष्टि नहीं होता है तो प्रोसेसिंग शुल्क वापस कर दिया जाता है। लोन केवल बिना शर्त प्रवेश ऑफर प्राप्त होने के बाद स्वीकृत किया जाता है।"),
        
        ("<b>Q3: क्या मैं लोन अनुमोदन के बाद संस्थान बदल सकता हूं?</b>",
         "हां, लेकिन आपको तुरंत बैंक को सूचित करना होगा। नया संस्थान अनुमोदित होना चाहिए और नए पाठ्यक्रम फीस के आधार पर लोन का पुनर्मूल्यांकन किया जा सकता है।"),
        
        ("<b>Q4: लोन राशि किसे मिलेगी - छात्र या संस्थान?</b>",
         "ट्यूशन फीस के लिए लोन सीधे संस्थान को भुगतान किया जाता है। छात्रावास, किताबें जैसे अन्य खर्चों के लिए, इसे छात्र खाते में दिया जा सकता है।"),
        
        ("<b>Q5: मैं EMI का भुगतान कब शुरू करूं?</b>",
         "EMI मोरेटोरियम अवधि (पाठ्यक्रम + 1 वर्ष या नौकरी के 6 महीने बाद) के बाद शुरू होती है। हालांकि, आप कुल लागत बचाने के लिए अध्ययन के दौरान स्वेच्छा से ब्याज का भुगतान शुरू कर सकते हैं।"),
        
        ("<b>Q6: यदि मुझे बाद में छात्रवृत्ति मिलती है तो क्या होगा?</b>",
         "तुरंत बैंक को सूचित करें। छात्रवृत्ति राशि को समायोजित किया जाएगा और लोन राशि कम की जा सकती है। यह आपके EMI बोझ को कम करने में मदद करता है।"),
        
        ("<b>Q7: यदि छात्र लोन उधारकर्ता है तो क्या माता-पिता कर लाभ का दावा कर सकते हैं?</b>",
         "80E के तहत कर लाभ केवल उस व्यक्ति को उपलब्ध है जिसने अपने नाम पर लोन लिया है। यदि लोन छात्र के नाम पर है, तो केवल छात्र दावा कर सकता है (एक बार वे कमाई शुरू करते हैं)।"),
        
        ("<b>Q8: यदि मुझे पाठ्यक्रम पूरा होने के बाद नौकरी नहीं मिलती है तो क्या होगा?</b>",
         "तुरंत बैंक को सूचित करें। हम मोरेटोरियम को 6 महीने से 1 वर्ष तक बढ़ा सकते हैं या लोन को पुनर्गठित कर सकते हैं। संचार महत्वपूर्ण है - चुपचाप डिफॉल्ट न करें।"),
        
        ("<b>Q9: क्या दूरस्थ शिक्षा या ऑनलाइन पाठ्यक्रमों के लिए लोन उपलब्ध है?</b>",
         "लोन मुख्य रूप से पूर्णकालिक नियमित पाठ्यक्रमों के लिए है। प्रतिष्ठित संस्थानों के कुछ ऑनलाइन/दूरस्थ पाठ्यक्रमों पर मामला-दर-मामला आधार पर विचार किया जा सकता है।"),
        
        ("<b>Q10: विदेशी विश्वविद्यालय के लिए कौन से दस्तावेज चाहिए?</b>",
         "बिना शर्त प्रवेश ऑफर, I-20/CAS/COE, IELTS/TOEFL/GRE स्कोर, पासपोर्ट, वीजा आवेदन, पूरे पाठ्यक्रम के लिए फीस संरचना, और माता-पिता के वित्तीय दस्तावेज।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Important Notes
    story.append(Paragraph("याद रखने योग्य महत्वपूर्ण बिंदु", heading_style))
    notes = [
        "• सह-उधारकर्ता (माता-पिता/अभिभावक) सभी एजुकेशन लोन के लिए अनिवार्य है।",
        "• प्रवेश UGC/AICTE/MCI अनुमोदित संस्थानों या मान्यता प्राप्त विदेशी विश्वविद्यालयों में होना चाहिए।",
        "• ब्याज पहले भुगतान की तारीख से अर्जित होना शुरू होता है, EMI शुरू होने की तारीख से नहीं।",
        "• मोरेटोरियम के दौरान, यदि भुगतान नहीं किया जाता है तो ब्याज चक्रवृद्धि होता है और मूलधन में जोड़ा जाता है।",
        "• अध्ययन अवधि के दौरान ब्याज का भुगतान करने से कुल लोन लागत में काफी कमी आती है।",
        "• विदेशी शिक्षा के लिए, लोन देश के मानदंडों के अनुसार ट्यूशन + रहने का खर्च कवर करता है।",
        "• मार्जिन मनी (5-15%) छात्र/माता-पिता द्वारा भुगतान की जानी चाहिए - लोन में कवर नहीं है।",
        "• लोन सेमेस्टर/वर्ष फीस भुगतान अनुसूची के आधार पर कई किस्तों में भुगतान किया जा सकता है।",
        "• पूर्व भुगतान को प्रोत्साहित किया जाता है - कोई शुल्क नहीं। ब्याज बोझ को काफी कम करने में मदद करता है।",
        "• समय पर EMI से अच्छा क्रेडिट स्कोर बनाए रखें - भविष्य के लोन (घर, कार, आदि) को प्रभावित करता है।",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>एजुकेशन लोन सहायता के लिए</b><br/>
    कस्टमर केयर: 1800-123-4567 | 080-1234-5678<br/>
    ईमेल: educationloans@sunnationalbank.in<br/>
    वेबसाइट: www.sunnationalbank.in/education-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>ज्ञान में निवेश करें - यह सबसे अच्छा ब्याज देता है!</i>
    </para>
    """
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "एजुकेशन लोन गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "एजुकेशन लोन गाइड"))
    return output_path


def create_business_loan_doc():
    """Create comprehensive Business Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "business_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#FF8F42'), spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("बिजनेस लोन", title_style))
    story.append(Paragraph("अपने व्यवसाय की वृद्धि को बढ़ावा दें - MSME और SME वित्तपोषण", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """सन नेशनल बैंक बिजनेस लोन माइक्रो, स्मॉल और मीडियम एंटरप्राइजेज (MSMEs) के लिए कार्यशील पूंजी की जरूरतों, विस्तार, उपकरण खरीद, या किसी भी व्यवसाय आवश्यकता को पूरा करने के लिए डिज़ाइन किया गया है। हम MUDRA लोन, टर्म लोन और कार्यशील पूंजी सुविधाओं सहित लचीले वित्तपोषण विकल्पों के साथ उद्यमियों का समर्थन करते हैं।"""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=8, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=7, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("MUDRA लोन", table_header_style), Paragraph("SME टर्म लोन", table_header_style), Paragraph("कार्यशील पूंजी", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("Rs. 10,000 - Rs. 10 लाख<br/>(शिशु/किशोर/तरुण)", table_cell_style), Paragraph("Rs. 10 लाख - Rs. 50 करोड़", table_cell_style), Paragraph("Rs. 5 लाख - Rs. 25 करोड़", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("7.50% - 10.00% प्रति वर्ष", table_cell_style), Paragraph("10.00% - 14.00% प्रति वर्ष", table_cell_style), Paragraph("11.00% - 15.00% प्रति वर्ष", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("7 वर्ष तक", table_cell_style), Paragraph("10 वर्ष तक", table_cell_style), Paragraph("12 महीने (नवीकरणीय)", table_cell_style)],
        [Paragraph("गारंटी", table_cell_style), Paragraph("आवश्यक नहीं<br/>(Rs. 10 लाख तक)", table_cell_style), Paragraph("Rs. 25 लाख से अधिक पर आवश्यक", table_cell_style), Paragraph("Rs. 50 लाख से अधिक पर आवश्यक", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("0.50% - 1% + GST", table_cell_style), Paragraph("1.5% - 2% + GST", table_cell_style), Paragraph("1% + GST", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[1.5*inch, 1.6*inch, 1.6*inch, 1.8*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("बिजनेस लोन के प्रकार", heading_style))
    loan_types = [
        "<b>1. MUDRA लोन:</b> माइक्रो उद्यमों के लिए सरकारी योजना। शिशु (Rs. 50,000 तक), किशोर (Rs. 50,001 से Rs. 5 लाख), तरुण (Rs. 5,00,001 से Rs. 10 लाख)।",
        "<b>2. टर्म लोन:</b> पूंजीगत व्यय के लिए - मशीनरी, उपकरण, फैक्टरी सेटअप, विस्तार। मासिक/त्रैमासिक EMI के साथ निश्चित अवधि।",
        "<b>3. कार्यशील पूंजी लोन:</b> दैनिक संचालन के लिए - कच्चा माल, वेतन, किराया। ओवरड्राफ्ट या कैश क्रेडिट सीमा सुविधा।",
        "<b>4. इनवॉइस फाइनेंसिंग:</b> लंबित इनवॉइस/बिलों के खिलाफ तत्काल धन प्राप्त करें। इनवॉइस मूल्य का 80% तक। केवल उपयोग की गई राशि पर ब्याज।",
        "<b>5. उपकरण वित्तपोषण:</b> मशीनरी, वाहन, कंप्यूटर, उपकरण वित्तपोषण। उपकरण गारंटी के रूप में कार्य करता है। 90% तक वित्तपोषण।",
        "<b>6. व्यवसाय ओवरड्राफ्ट:</b> अनुमोदित सीमा तक आवश्यकतानुसार धन निकालें। केवल उपयोग की गई राशि पर ब्याज, पूरी सीमा पर नहीं।",
    ]
    for ltype in loan_types:
        story.append(Paragraph(ltype, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("आवश्यकता", eligibility_header_style)],
        [Paragraph("व्यवसाय प्रकार", eligibility_cell_style), Paragraph("स्वामित्व, साझेदारी, प्राइवेट लिमिटेड, LLP, सहकारी समितियां", eligibility_cell_style)],
        [Paragraph("व्यवसाय विन्टेज", eligibility_cell_style), Paragraph("न्यूनतम 2 वर्ष (Rs. 50 लाख से अधिक के लोन के लिए 3 वर्ष)", eligibility_cell_style)],
        [Paragraph("टर्नओवर", eligibility_cell_style), Paragraph("MUDRA: कोई न्यूनतम नहीं<br/>SME: न्यूनतम Rs. 10 लाख प्रति वर्ष<br/>बड़ा: आवश्यकता के अनुसार", eligibility_cell_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("स्वामी/साझेदार: 21-65 वर्ष", eligibility_cell_style)],
        [Paragraph("GST पंजीकरण", eligibility_cell_style), Paragraph("टर्नओवर > Rs. 40 लाख या GST अधिनियम के अनुसार अनिवार्य", eligibility_cell_style)],
        [Paragraph("ITR दाखिल करना", eligibility_cell_style), Paragraph("पिछले 2 वर्षों के ITR अनिवार्य (बड़े लोन के लिए 3 वर्ष)", eligibility_cell_style)],
        [Paragraph("CIBIL स्कोर", eligibility_cell_style), Paragraph("न्यूनतम 650 (व्यवसाय और व्यक्तिगत)<br/>सर्वोत्तम दरों के लिए 700+", eligibility_cell_style)],
        [Paragraph("लाभप्रदता", eligibility_cell_style), Paragraph("व्यवसाय पिछले कम से कम 1 वर्ष से लाभदायक होना चाहिए", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[2*inch, 4.5*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    docs_list = [
        "• <b>KYC:</b> सभी साझेदारों/निदेशकों का आधार, PAN (अनिवार्य)",
        "• <b>व्यवसाय प्रमाण:</b> GST पंजीकरण, दुकान/प्रतिष्ठान लाइसेंस, MSME/उद्योग आधार प्रमाणपत्र",
        "• <b>वित्तीय दस्तावेज:</b> आय गणना के साथ पिछले 2-3 वर्षों के ITR, लेखा परीक्षित वित्तीय (P&L, बैलेंस शीट)",
        "• <b>बैंक स्टेटमेंट:</b> व्यवसाय लेनदेन दिखाने वाला पिछले 12 महीने का चालू खाता स्टेटमेंट",
        "• <b>व्यवसाय प्रोफ़ाइल:</b> कंपनी प्रोफ़ाइल, ग्राहकों की सूची, खरीद आदेश, चल रहे अनुबंध",
        "• <b>स्वामित्व प्रमाण:</b> कार्यालय/फैक्टरी स्वामित्व दस्तावेज या NOC के साथ किराया समझौता",
        "• <b>अनुमानित वित्तीय:</b> नए विस्तार के लिए - विस्तृत परियोजना रिपोर्ट, अनुमानित लागत",
        "• <b>गारंटी दस्तावेज:</b> प्रॉपर्टी कागज, मूल्यांकन रिपोर्ट (यदि गारंटी दे रहे हैं)",
        "• <b>मौजूदा लोन:</b> मौजूदा व्यवसाय लोन के अनुमोदन पत्र और स्टेटमेंट",
    ]
    for doc_item in docs_list:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("लोन राशि का 0.50% - 2% + GST (लोन प्रकार के आधार पर)", fees_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", fees_cell_style), Paragraph("2% - 4% + GST (यदि 12 महीने से पहले पूर्व भुगतान किया गया है)<br/>12 महीने के बाद शून्य", fees_cell_style)],
        [Paragraph("देर से भुगतान", fees_cell_style), Paragraph("बकाया राशि पर प्रति माह 2% - 3%", fees_cell_style)],
        [Paragraph("दंडात्मक ब्याज", fees_cell_style), Paragraph("डिफॉल्ट राशि पर अतिरिक्त 2% प्रति वर्ष", fees_cell_style)],
        [Paragraph("दस्तावेज शुल्क", fees_cell_style), Paragraph("Rs. 500 - Rs. 2,000 + GST", fees_cell_style)],
        [Paragraph("कानूनी/तकनीकी शुल्क", fees_cell_style), Paragraph("वास्तविक के अनुसार (Rs. 2,000 - Rs. 10,000)", fees_cell_style)],
        [Paragraph("inspection शुल्क", fees_cell_style), Paragraph("परियोजना लोन के लिए प्रति निरीक्षण Rs. 1,000", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: MUDRA लोन क्या है?</b>", "MUDRA (माइक्रो यूनिट्स डेवलपमेंट और रिफाइनेंस एजेंसी) बिना गारंटी के Rs. 10 लाख तक के माइक्रो उद्यमों के लिए सरकारी योजना है।"),
        ("<b>Q2: क्या स्टार्टअप बिजनेस लोन के लिए आवेदन कर सकते हैं?</b>", "हां, लेकिन न्यूनतम 2 वर्ष का व्यवसाय विन्टेज आवश्यक है। नए स्टार्टअप के लिए, Startup India या PMEGP जैसी सरकारी योजनाओं का अन्वेषण करें।"),
        ("<b>Q3: क्या GST पंजीकरण अनिवार्य है?</b>", "हां, यदि आपका टर्नओवर Rs. 40 लाख से अधिक है या GST अधिनियम के अनुसार है। MUDRA के तहत छोटे व्यवसायों के लिए, अनिवार्य नहीं हो सकता है।"),
        ("<b>Q4: कार्यशील पूंजी लोन क्या है?</b>", "यह दैनिक संचालन के लिए एक क्रेडिट सुविधा है। आपको एक सीमा मिलती है और आवश्यकतानुसार निकाल सकते हैं। केवल उपयोग की गई राशि पर ब्याज लगाया जाता है।"),
        ("<b>Q5: क्या मैं व्यवसाय हानि के लिए लोन प्राप्त कर सकता हूं?</b>", "नहीं, लोन वृद्धि और विस्तार के लिए है। व्यवसाय लाभप्रदता दिखाना चाहिए। हानि करने वाले व्यवसाय उच्च जोखिम वाले हैं और आम तौर पर वित्तपोषित नहीं होते हैं।"),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    contact_text = """<para align=center><b>बिजनेस लोन सहायता के लिए</b><br/>कस्टमर केयर: 1800-123-4567<br/>ईमेल: businessloans@sunnationalbank.in<br/>वेबसाइट: www.sunnationalbank.in/business-loan</para>"""
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "बिजनेस लोन गाइड"), onLaterPages=lambda c, d: create_header_footer(c, d, "बिजनेस लोन गाइड"))
    return output_path


def create_gold_loan_doc():
    """Create comprehensive Gold Loan product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "gold_loan_product_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#FF8F42'), spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("गोल्ड लोन", title_style))
    story.append(Paragraph("अपने सोने के आभूषणों के खिलाफ तत्काल नकदी - तत्काल अनुमोदन", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """अपने सोने के आभूषणों/सिक्कों/बार को गिरवी रखकर तत्काल नकदी प्राप्त करें। सन नेशनल बैंक गोल्ड लोन RBI दिशानिर्देशों के अनुसार सोने के मूल्य का 75% तक लचीले चुकौती विकल्पों के साथ प्रदान करता है। आपका सोना पूर्ण बीमा कवरेज के साथ बैंक लॉकर में सुरक्षित रूप से संग्रहीत किया जाता है।"""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=10, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("विवरण", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("Rs. 10,000 से Rs. 1 करोड़ (सोने के मूल्य के आधार पर)", table_cell_style)],
        [Paragraph("लोन-टू-वैल्यू (LTV)", table_cell_style), Paragraph("सोने के मूल्य का 75% तक (RBI मानदंडों के अनुसार)", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("7.00% - 12.00% प्रति वर्ष (राशि और अवधि के आधार पर)", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("3 महीने से 36 महीने", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("0.50% - 1% + GST (न्यूनतम Rs. 500)", table_cell_style)],
        [Paragraph("स्वीकृत सोने की शुद्धता", table_cell_style), Paragraph("18 कैरेट से 24 कैरेट सोना", table_cell_style)],
        [Paragraph("भुगतान समय", table_cell_style), Paragraph("सोने के सत्यापन के 30 मिनट के भीतर", table_cell_style)],
        [Paragraph("पूर्व भुगतान", table_cell_style), Paragraph("कभी भी बिना शुल्क के अनुमति", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("स्वीकृत सोने के प्रकार", heading_style))
    gold_types = [
        "• <b>सोने के आभूषण:</b> हार, चूड़ियां, चेन, अंगूठी, ईयररिंग (18K - 24K शुद्धता होनी चाहिए)",
        "• <b>सोने के सिक्के:</b> बैंकों या प्रमाणित डीलरों से खरीदे गए सिक्के (शुद्धता प्रमाणपत्र आवश्यक)",
        "• <b>सोने के बार/बिस्कुट:</b> मान्यता प्राप्त एजेंसियों से शुद्धता हॉलमार्क वाले सोने के बार",
        "• <b>नोट:</b> जड़े हुए आभूषण केवल सोने के वजन के आधार पर स्वीकार किए जाते हैं (पत्थर का मूल्य नहीं माना जाता)",
    ]
    for gtype in gold_types:
        story.append(Paragraph(gtype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("चुकौती विकल्प", heading_style))
    repay_options = [
        "<b>1. नियमित EMI:</b> हर महीने निश्चित EMI का भुगतान करें (मूलधन + ब्याज)",
        "<b>2. बुलेट चुकौती:</b> केवल मासिक ब्याज का भुगतान करें, अंत में पूरा मूलधन चुकाएं",
        "<b>3. ब्याज सेवा:</b> समय-समय पर ब्याज का भुगतान करें, कभी भी मूलधन बंद करें",
        "<b>4. एक बार का भुगतान:</b> लोन परिपक्वता पर ब्याज और मूलधन एक साथ चुकाएं",
    ]
    for option in repay_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("पात्रता और दस्तावेज", heading_style))
    eligibility = [
        "• <b>आयु:</b> 18 से 70 वर्ष",
        "• <b>KYC दस्तावेज:</b> आधार कार्ड, PAN कार्ड",
        "• <b>स्वामित्व प्रमाण:</b> सोने की खरीद बिल/इनवॉइस (यदि उपलब्ध है - अनिवार्य नहीं)",
        "• <b>आय प्रमाण:</b> आवश्यक नहीं - लोन सोने की गारंटी के खिलाफ है",
        "• <b>क्रेडिट स्कोर:</b> आवश्यक नहीं - सोना सुरक्षा के रूप में कार्य करता है",
    ]
    for elig in eligibility:
        story.append(Paragraph(elig, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("सोना मूल्यांकन प्रक्रिया", heading_style))
    valuation = [
        "<b>चरण 1:</b> गैर-विनाशकारी XRF मशीन का उपयोग करके सोने के आभूषणों की शुद्धता का परीक्षण किया जाता है (आभूषणों को कोई नुकसान नहीं)",
        "<b>चरण 2:</b> प्रमाणित इलेक्ट्रॉनिक वजन मशीन पर वजन मापा जाता है",
        "<b>चरण 3:</b> लोन मूल्य की गणना: वजन × शुद्धता % × वर्तमान सोना दर × LTV (75%)",
        "<b>चरण 4:</b> बैंक की दर सूची के अनुसार सोना दर (बाजार मूल्य के आधार पर)",
        "<b>उदाहरण:</b> 22K सोने के 100 ग्राम @ Rs. 6,000/ग्राम = Rs. 6,00,000 मूल्य। लोन: 75% = Rs. 4,50,000",
    ]
    for val in valuation:
        story.append(Paragraph(val, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("0.50% - 1% + GST (न्यूनतम Rs. 500, अधिकतम Rs. 10,000)", fees_cell_style)],
        [Paragraph("पूर्व भुगतान/फोरक्लोजर", fees_cell_style), Paragraph("शून्य - बिना शुल्क के कभी भी बंद करें", fees_cell_style)],
        [Paragraph("देर से भुगतान शुल्क", fees_cell_style), Paragraph("बकाया राशि पर प्रति माह 2%", fees_cell_style)],
        [Paragraph("मूल्यांकन शुल्क", fees_cell_style), Paragraph("मुफ्त - कोई सोना परीक्षण शुल्क नहीं", fees_cell_style)],
        [Paragraph("भंडारण और बीमा", fees_cell_style), Paragraph("मुफ्त - बैंक सभी भंडारण और बीमा लागत वहन करता है", fees_cell_style)],
        [Paragraph("डुप्लिकेट दस्तावेज", fees_cell_style), Paragraph("प्रति दस्तावेज Rs. 100", fees_cell_style)],
        [Paragraph("लोन नवीकरण शुल्क", fees_cell_style), Paragraph("Rs. 500 + GST (यदि अवधि बढ़ाई गई है)", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("लोन बंद और सोना वापसी", heading_style))
    closure_process = [
        "• पूरी बकाया राशि का भुगतान करें (मूलधन + ब्याज + शुल्क)",
        "• भुगतान निकासी के 30 मिनट के भीतर सोना वापस किया जाता है",
        "• आभूषणों को सत्यापित करें - पहचान चिह्नों के साथ समान वस्तुएं वापस की जाएंगी",
        "• बैंक से लोन बंद प्रमाणपत्र और NOC प्राप्त करें",
        "• आंशिक रिलीज: आनुपातिक राशि का भुगतान करें और कुछ सोने की वस्तुओं को रिलीज करें",
    ]
    for step in closure_process:
        story.append(Paragraph(step, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("महत्वपूर्ण नियम और शर्तें", heading_style))
    terms = [
        "• RBI दिशानिर्देश: सभी गोल्ड लोन के लिए अधिकतम LTV सोने के मूल्य का 75% है",
        "• सोना पूर्ण बीमा कवरेज के साथ बैंक के सुरक्षित लॉकर में संग्रहीत किया जाता है",
        "• यदि 12 महीने तक EMI का भुगतान नहीं किया जाता है, तो बैंक को सोना नीलाम करने का अधिकार है (उचित नोटिस के बाद)",
        "• नीलामी अधिशेष (यदि कोई हो) दायित्वों को समायोजित करने के बाद ग्राहक को वापस किया जाएगा",
        "• ब्याज दर लोन अवधि के लिए निश्चित है - सोना दर उतार-चढ़ाव से जुड़ा नहीं है",
        "• सोने के आभूषण केवल नीलामी के मामले में पिघलाए जाएंगे, अन्यथा नहीं",
        "• ग्राहक अतिरिक्त सोना गिरवी रखकर कभी भी लोन टॉप-अप कर सकता है",
        "• जल्दी बंद करने को प्रोत्साहित किया जाता है - कोई पूर्व भुगतान शुल्क नहीं",
        "• पारदर्शिता के लिए सोने का फोटो/वीडियो दस्तावेजीकरण किया जाता है",
    ]
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: क्या परीक्षण के दौरान मेरे सोने के आभूषण खराब हो जाएंगे?</b>", "नहीं, हम XRF तकनीक का उपयोग करते हैं जो गैर-विनाशकारी है। आपके आभूषण बरकरार रहते हैं।"),
        ("<b>Q2: यदि लोन लेने के बाद सोना दर बढ़ जाती है तो क्या होगा?</b>", "आपकी EMI और ब्याज समान रहता है। सोना दर उतार-चढ़ाव मौजूदा लोन शर्तों को प्रभावित नहीं करता है।"),
        ("<b>Q3: क्या मैं उसी सोने पर अतिरिक्त लोन ले सकता हूं?</b>", "नहीं, लेकिन आप मौजूदा लोन बंद कर सकते हैं और वर्तमान दरों पर नया लोन ले सकते हैं। या टॉप-अप के लिए अतिरिक्त सोना गिरवी रखें।"),
        ("<b>Q4: क्या हॉलमार्क सोना अनिवार्य है?</b>", "अनिवार्य नहीं है। हम XRF मशीन का उपयोग करके शुद्धता का परीक्षण करते हैं। लेकिन हॉलमार्क तेजी से प्रसंस्करण में मदद करता है।"),
        ("<b>Q5: यदि मैं चुकौती नहीं करता हूं तो क्या होगा?</b>", "12 महीने के डिफॉल्ट के बाद, बैंक RBI दिशानिर्देशों के अनुसार सोना नीलाम कर सकता है। नीलामी से पहले नोटिस भेजा जाएगा।"),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    contact_text = """<para align=center><b>गोल्ड लोन सहायता के लिए</b><br/>कस्टमर केयर: 1800-123-4567<br/>ईमेल: goldloan@sunnationalbank.in<br/>वेबसाइट: www.sunnationalbank.in/gold-loan<br/><i>30 मिनट में तत्काल नकदी प्राप्त करें!</i></para>"""
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "गोल्ड लोन गाइड"), onLaterPages=lambda c, d: create_header_footer(c, d, "गोल्ड लोन गाइड"))
    return output_path


def create_loan_against_property_doc():
    """Create comprehensive Loan Against Property product documentation in Hindi"""
    output_path = Path(__file__).parent / "loan_products_hindi" / "loan_against_property_guide.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName=HINDI_FONT_BOLD)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName=HINDI_FONT_BOLD)
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#FF8F42'), spaceAfter=8, spaceBefore=8, fontName=HINDI_FONT_BOLD)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10, fontName=HINDI_FONT)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6, fontName=HINDI_FONT)
    
    story.append(Paragraph("प्रॉपर्टी के खिलाफ लोन (LAP)", title_style))
    story.append(Paragraph("किसी भी उद्देश्य के लिए अपनी प्रॉपर्टी के मूल्य को अनलॉक करें - व्यवसाय या व्यक्तिगत", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("उत्पाद अवलोकन", heading_style))
    overview_text = """प्रॉपर्टी के खिलाफ लोन (LAP) आपको किसी भी वित्तीय आवश्यकता को पूरा करने के लिए अपनी आवासीय या वाणिज्यिक प्रॉपर्टी का लाभ उठाने की अनुमति देता है - व्यवसाय विस्तार, कार्यशील पूंजी, शिक्षा, चिकित्सा आपातकाल, या ऋण समेकन। प्रॉपर्टी आपके कब्जे में रहती है जबकि आपको आकर्षक ब्याज दरों पर पर्याप्त धन मिलता है।"""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                      fontSize=9, fontName=HINDI_FONT_BOLD,
                                      textColor=colors.whitesmoke, alignment=TA_LEFT)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                     fontSize=8, fontName=HINDI_FONT,
                                     alignment=TA_LEFT)
    
    features = [
        [Paragraph("विशेषता", table_header_style), Paragraph("आवासीय प्रॉपर्टी", table_header_style), Paragraph("वाणिज्यिक प्रॉपर्टी", table_header_style)],
        [Paragraph("लोन राशि", table_cell_style), Paragraph("Rs. 5 लाख से Rs. 10 करोड़", table_cell_style), Paragraph("Rs. 10 लाख से Rs. 25 करोड़", table_cell_style)],
        [Paragraph("LTV (लोन टू वैल्यू)", table_cell_style), Paragraph("बाजार मूल्य का 60% तक", table_cell_style), Paragraph("बाजार मूल्य का 55% तक", table_cell_style)],
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("9.00% - 12.00% प्रति वर्ष", table_cell_style), Paragraph("10.00% - 14.00% प्रति वर्ष", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("20 वर्ष तक", table_cell_style), Paragraph("15 वर्ष तक", table_cell_style)],
        [Paragraph("प्रोसेसिंग शुल्क", table_cell_style), Paragraph("लोन राशि का 1% - 2% + GST", table_cell_style), Paragraph("1.5% - 2.5% + GST", table_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", table_cell_style), Paragraph("12 महीने के बाद शून्य<br/>12 महीने के भीतर 4% + GST", table_cell_style), Paragraph("18 महीने के बाद शून्य<br/>18 महीने के भीतर 5% + GST", table_cell_style)],
        [Paragraph("उपयोग", table_cell_style), Paragraph("कोई भी व्यक्तिगत या व्यवसाय उद्देश्य", table_cell_style), Paragraph("मुख्य रूप से व्यवसाय उद्देश्य", table_cell_style)],
    ]
    
    features_table = Table(features, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("स्वीकृत प्रॉपर्टियों के प्रकार", heading_style))
    property_types = [
        "<b>आवासीय:</b> स्व-कब्जे या किराए पर - अपार्टमेंट, स्वतंत्र घर, विला, बंगले (स्पष्ट स्वामित्व होना चाहिए)",
        "<b>वाणिज्यिक:</b> कार्यालय, दुकानें, शोरूम, गोदाम, औद्योगिक शेड (किराए पर या स्व-उपयोग)",
        "<b>प्लॉट/भूमि:</b> अनुमोदित योजनाओं के साथ आवासीय या वाणिज्यिक प्लॉट (कुछ मामलों में)",
        "<b>नोट:</b> प्रॉपर्टी उधारकर्ता के नाम या सह-आवेदक के नाम पर होनी चाहिए। कृषि भूमि स्वीकार नहीं की जाती है।",
    ]
    for ptype in property_types:
        story.append(Paragraph(ptype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility_header_style = ParagraphStyle('EligibilityHeader', parent=styles['Normal'],
                                             fontSize=9, fontName=HINDI_FONT_BOLD,
                                             textColor=colors.whitesmoke, alignment=TA_LEFT)
    eligibility_cell_style = ParagraphStyle('EligibilityCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    eligibility = [
        [Paragraph("मानदंड", eligibility_header_style), Paragraph("वेतनभोगी", eligibility_header_style), Paragraph("स्व-नियोजित/व्यवसाय", eligibility_header_style)],
        [Paragraph("आयु", eligibility_cell_style), Paragraph("21 - 65 वर्ष", eligibility_cell_style), Paragraph("25 - 70 वर्ष", eligibility_cell_style)],
        [Paragraph("आय", eligibility_cell_style), Paragraph("न्यूनतम Rs. 50,000 प्रति माह", eligibility_cell_style), Paragraph("न्यूनतम Rs. 6 लाख प्रति वर्ष (ITR)", eligibility_cell_style)],
        [Paragraph("काम का अनुभव", eligibility_cell_style), Paragraph("न्यूनतम 2 वर्ष कुल", eligibility_cell_style), Paragraph("व्यवसाय में न्यूनतम 3 वर्ष", eligibility_cell_style)],
        [Paragraph("क्रेडिट स्कोर", eligibility_cell_style), Paragraph("न्यूनतम 700 (सर्वोत्तम दरों के लिए 750+)", eligibility_cell_style), Paragraph("न्यूनतम 700 (सर्वोत्तम दरों के लिए 750+)", eligibility_cell_style)],
        [Paragraph("प्रॉपर्टी आयु", eligibility_cell_style), Paragraph("लोन परिपक्वता पर 30 वर्ष तक", eligibility_cell_style), Paragraph("लोन परिपक्वता पर 25 वर्ष तक", eligibility_cell_style)],
        [Paragraph("स्वामित्व", eligibility_cell_style), Paragraph("स्व-स्वामित्व या सह-आवेदक स्वामित्व", eligibility_cell_style), Paragraph("स्व/कंपनी/साझेदारी स्वामित्व", eligibility_cell_style)],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("आवश्यक दस्तावेज", heading_style))
    story.append(Paragraph("व्यक्तिगत दस्तावेज:", subheading_style))
    personal_docs = [
        "• KYC: आधार कार्ड, PAN कार्ड (अनिवार्य)",
        "• आय प्रमाण: पिछले 6 महीने के वेतन स्लिप / आय गणना के साथ पिछले 2 वर्षों के ITR",
        "• बैंक स्टेटमेंट: सभी परिचालन खातों के लिए पिछले 12 महीने",
        "• रोजगार प्रमाण: रोजगार पत्र, व्यवसाय पंजीकरण प्रमाणपत्र",
    ]
    for doc_item in personal_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Paragraph("प्रॉपर्टी दस्तावेज:", subheading_style))
    property_docs = [
        "• बिक्री दस्तावेज/स्वामित्व दस्तावेज - स्पष्ट स्वामित्व दिखाने वाली पंजीकृत प्रति",
        "• स्वामित्व श्रृंखला - पिछले बिक्री दस्तावेज (राज्य के अनुसार पिछले 13-30 वर्ष)",
        "• बाध्यता प्रमाणपत्र (EC) - कोई लंबित दायित्व न दिखाने वाला पिछले 13-30 वर्ष",
        "• प्रॉपर्टी कर रसीदें - नवीनतम भुगतान रसीदें",
        "• भवन अनुमोदन योजना - नगर निगम अनुमोदित योजना",
        "• अधिवास प्रमाणपत्र / पूर्णता प्रमाणपत्र",
        "• बिल्डर/सोसाइटी से NOC (यदि लागू हो)",
        "• प्रॉपर्टी मूल्यांकन रिपोर्ट - बैंक पैनल वैल्यूअर निरीक्षण करेगा",
        "• यदि गिरवी रखा गया है: मौजूदा ऋणदाता से NOC या लोन बंद प्रमाणपत्र",
    ]
    for doc_item in property_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("लोन प्रसंस्करण चरण", heading_style))
    stages = [
        "<b>चरण 1 - आवेदन:</b> KYC और आय दस्तावेजों के साथ आवेदन जमा करें",
        "<b>चरण 2 - प्रॉपर्टी मूल्यांकन:</b> बैंक पैनल इंजीनियर प्रॉपर्टी का निरीक्षण करता है (3-5 दिन)",
        "<b>चरण 3 - कानूनी सत्यापन:</b> बैंक वकील सभी प्रॉपर्टी दस्तावेजों को सत्यापित करता है (7-10 दिन)",
        "<b>चरण 4 - तकनीकी सत्यापन:</b> तकनीकी टीम भवन गुणवत्ता, आयु, अनुपालन सत्यापित करती है",
        "<b>चरण 5 - क्रेडिट मूल्यांकन:</b> आय, CIBIL, चुकौती क्षमता का मूल्यांकन",
        "<b>चरण 6 - अनुमोदन:</b> राशि, दर, अवधि विवरण के साथ लोन अनुमोदित",
        "<b>चरण 7 - दस्तावेजीकरण:</b> लोन समझौता, गिरवी दस्तावेज निष्पादित और पंजीकृत",
        "<b>चरण 8 - भुगतान:</b> सभी दस्तावेजीकरण के बाद बैंक खाते में राशि जमा",
    ]
    for stage in stages:
        story.append(Paragraph(stage, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("शुल्क और चार्ज", heading_style))
    fees_header_style = ParagraphStyle('FeesHeader', parent=styles['Normal'],
                                     fontSize=9, fontName=HINDI_FONT_BOLD,
                                     textColor=colors.whitesmoke, alignment=TA_LEFT)
    fees_cell_style = ParagraphStyle('FeesCell', parent=styles['Normal'],
                                   fontSize=8, fontName=HINDI_FONT,
                                   alignment=TA_LEFT)
    
    fees_data = [
        [Paragraph("शुल्क प्रकार", fees_header_style), Paragraph("राशि", fees_header_style)],
        [Paragraph("प्रोसेसिंग शुल्क", fees_cell_style), Paragraph("लोन राशि का 1% - 2.5% + GST", fees_cell_style)],
        [Paragraph("प्रॉपर्टी मूल्यांकन", fees_cell_style), Paragraph("Rs. 3,000 - Rs. 10,000 (प्रॉपर्टी मूल्य के आधार पर)", fees_cell_style)],
        [Paragraph("कानूनी शुल्क", fees_cell_style), Paragraph("Rs. 5,000 - Rs. 15,000 + गिरवी दस्तावेज पर स्टाम्प ड्यूटी", fees_cell_style)],
        [Paragraph("पूर्व भुगतान शुल्क", fees_cell_style), Paragraph("12-18 महीने के बाद शून्य<br/>12-18 महीने के भीतर 4-5% + GST", fees_cell_style)],
        [Paragraph("देर से भुगतान शुल्क", fees_cell_style), Paragraph("बकाया पर प्रति माह 2% या Rs. 500 (जो भी अधिक हो)", fees_cell_style)],
        [Paragraph("NACH बाउंस", fees_cell_style), Paragraph("प्रति बाउंस Rs. 500", fees_cell_style)],
        [Paragraph("आंशिक भुगतान शुल्क", fees_cell_style), Paragraph("शून्य - कभी भी एकमुश्त भुगतान करें", fees_cell_style)],
        [Paragraph("डुप्लिकेट दस्तावेज", fees_cell_style), Paragraph("प्रति दस्तावेज सेट Rs. 500", fees_cell_style)],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: क्या मैं पैसे का उपयोग किसी भी उद्देश्य के लिए कर सकता हूं?</b>", "हां, LAP बहुउद्देशीय लोन है। व्यवसाय, शिक्षा, चिकित्सा, विवाह, या किसी भी अन्य वैध उद्देश्य के लिए उपयोग करें। कोई प्रतिबंध नहीं।"),
        ("<b>Q2: क्या मुझे प्रॉपर्टी खाली करनी होगी?</b>", "नहीं, प्रॉपर्टी आपके कब्जे में रहती है। बैंक केवल लोन चुकाने तक गिरवी अधिकार रखता है। आप इसमें रह सकते हैं/उपयोग कर सकते हैं/किराए पर दे सकते हैं।"),
        ("<b>Q3: प्रॉपर्टी मूल्य कैसे निर्धारित किया जाता है?</b>", "बैंक पैनल वैल्यूअर प्रॉपर्टी का निरीक्षण करता है और स्थान, आकार, आयु, बाजार दरों और स्थिति के आधार पर मूल्यांकन रिपोर्ट प्रदान करता है।"),
        ("<b>Q4: क्या मैं किसी और के नाम पर प्रॉपर्टी गिरवी रख सकता हूं?</b>", "प्रॉपर्टी आपके नाम या सह-आवेदक के नाम पर होनी चाहिए। सह-स्वामी को लोन में सह-आवेदक होना चाहिए।"),
        ("<b>Q5: यदि मेरे पास पहले से ही प्रॉपर्टी पर होम लोन है तो क्या होगा?</b>", "मौजूदा लोन वाली प्रॉपर्टी स्वीकार नहीं की जाती है। आपको पहले मौजूदा लोन बंद करना होगा या हमारे बैंक में बैलेंस ट्रांसफर + टॉप-अप करना होगा।"),
        ("<b>Q6: क्या प्रॉपर्टी बीमा अनिवार्य है?</b>", "हां, प्रॉपर्टी को आग, भूकंप और अन्य प्राकृतिक आपदाओं के खिलाफ बैंक को को-लाभार्थी के रूप में बीमा करना होगा।"),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("महत्वपूर्ण नियम", heading_style))
    terms = [
        "• प्रॉपर्टी में स्पष्ट और विपणन योग्य स्वामित्व होना चाहिए - सभी बाधाओं से मुक्त",
        "• लोन अवधि + प्रॉपर्टी आयु 50 वर्ष से अधिक नहीं होनी चाहिए",
        "• बैंक को को-लाभार्थी के रूप में प्रॉपर्टी बीमा अनिवार्य है",
        "• गिरवी दस्तावेज को उप-रजिस्ट्रार कार्यालय में पंजीकृत करना होगा (ग्राहक स्टाम्प ड्यूटी वहन करता है)",
        "• 3 लगातार महीनों के लिए डिफॉल्ट बैंक को SARFAESI अधिनियम लागू करने का अधिकार देता है",
        "• SARFAESI के तहत, बैंक 60 दिनों के नोटिस के बाद अदालती आदेश के बिना कब्जा ले सकता है और प्रॉपर्टी बेच सकता है",
        "• लोन पूरी तरह से चुकाने और गिरवी रिलीज होने तक प्रॉपर्टी को बेचा या स्थानांतरित नहीं किया जा सकता है",
        "• ब्याज दर पूरी अवधि के लिए निश्चित है - कोई फ्लोटिंग दर विकल्प नहीं",
    ]
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    contact_text = """<para align=center><b>प्रॉपर्टी के खिलाफ लोन के लिए</b><br/>कस्टमर केयर: 1800-123-4567<br/>ईमेल: lap@sunnationalbank.in<br/>वेबसाइट: www.sunnationalbank.in/loan-against-property</para>"""
    story.append(Paragraph(contact_text, normal_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "प्रॉपर्टी के खिलाफ लोन गाइड"), onLaterPages=lambda c, d: create_header_footer(c, d, "प्रॉपर्टी के खिलाफ लोन गाइड"))
    return output_path


if __name__ == "__main__":
    print("सन नेशनल बैंक के लिए हिंदी में व्यापक लोन उत्पाद दस्तावेज बनाना...")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "loan_products_hindi"
    output_dir.mkdir(exist_ok=True)
    
    docs_created = []
    
    print("\n1️⃣  होम लोन उत्पाद गाइड बनाना...")
    home_loan_path = create_home_loan_doc()
    docs_created.append(("होम लोन", home_loan_path))
    print(f"   ✓ बनाया गया: {home_loan_path.name}")
    
    print("\n2️⃣  पर्सनल लोन उत्पाद गाइड बनाना...")
    personal_loan_path = create_personal_loan_doc()
    docs_created.append(("पर्सनल लोन", personal_loan_path))
    print(f"   ✓ बनाया गया: {personal_loan_path.name}")
    
    print("\n3️⃣  ऑटो लोन उत्पाद गाइड बनाना...")
    auto_loan_path = create_auto_loan_doc()
    docs_created.append(("ऑटो लोन", auto_loan_path))
    print(f"   ✓ बनाया गया: {auto_loan_path.name}")
    
    print("\n4️⃣  एजुकेशन लोन उत्पाद गाइड बनाना...")
    education_loan_path = create_education_loan_doc()
    docs_created.append(("एजुकेशन लोन", education_loan_path))
    print(f"   ✓ बनाया गया: {education_loan_path.name}")
    
    print("\n5️⃣  बिजनेस लोन उत्पाद गाइड बनाना...")
    business_loan_path = create_business_loan_doc()
    docs_created.append(("बिजनेस लोन", business_loan_path))
    print(f"   ✓ बनाया गया: {business_loan_path.name}")
    
    print("\n6️⃣  गोल्ड लोन उत्पाद गाइड बनाना...")
    gold_loan_path = create_gold_loan_doc()
    docs_created.append(("गोल्ड लोन", gold_loan_path))
    print(f"   ✓ बनाया गया: {gold_loan_path.name}")
    
    print("\n7️⃣  प्रॉपर्टी के खिलाफ लोन गाइड बनाना...")
    lap_path = create_loan_against_property_doc()
    docs_created.append(("प्रॉपर्टी के खिलाफ लोन", lap_path))
    print(f"   ✓ बनाया गया: {lap_path.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ सफलतापूर्वक {len(docs_created)} व्यापक लोन उत्पाद गाइड बनाए गए!")
    print(f"📁 स्थान: {output_dir}")
    print("\n📚 RAG के लिए बनाए गए दस्तावेज:")
    for idx, (loan_type, path) in enumerate(docs_created, 1):
        print(f"   {idx}. {loan_type}: {path.name}")

