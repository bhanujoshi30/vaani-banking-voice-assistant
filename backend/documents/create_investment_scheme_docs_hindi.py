# -*- coding: utf-8 -*-
"""
Create Comprehensive Investment Scheme Documentation in Hindi for RAG
These PDFs contain detailed information about each investment scheme offered by Sun National Bank in Hindi
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
                        if file.endswith('.ttc'):
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
                # For .ttc files, extract using fonttools
                try:
                    from fontTools.ttLib import TTFont as FontToolsTTFont
                    ttc = FontToolsTTFont(font_path, fontNumber=0)
                    fonts_dir = Path(__file__).parent / "fonts"
                    fonts_dir.mkdir(exist_ok=True)
                    temp_ttf = fonts_dir / f"extracted_{os.path.basename(font_path).replace('.ttc', '.ttf')}"
                    ttc.save(str(temp_ttf))
                    pdfmetrics.registerFont(TTFont('HindiFont', str(temp_ttf)))
                    print(f"✅ Extracted and registered Hindi font from TTC: {font_path}")
                    font_path = str(temp_ttf)
                except ImportError:
                    print(f"⚠️  fonttools not available. Install with: pip install fonttools")
                    continue
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
                    from fontTools.ttLib import TTFont as FontToolsTTFont
                    ttc = FontToolsTTFont(bold_path, fontNumber=0)
                    fonts_dir = Path(__file__).parent / "fonts"
                    temp_bold = fonts_dir / f"extracted_{os.path.basename(bold_path).replace('.ttc', '.ttf')}"
                    ttc.save(str(temp_bold))
                    pdfmetrics.registerFont(TTFont('HindiFontBold', str(temp_bold)))
                else:
                    pdfmetrics.registerFont(TTFont('HindiFontBold', bold_path))
                print(f"✅ Registered Hindi bold font")
                return 'HindiFont', 'HindiFontBold'
            else:
                # Use same font for bold
                pdfmetrics.registerFont(TTFont('HindiFontBold', font_path))
                return 'HindiFont', 'HindiFontBold'
        except Exception as e:
            print(f"⚠️  Failed to register {font_path}: {e}")
            continue
    
    print("⚠️  WARNING: No Hindi fonts found. Hindi text may not render correctly.")
    print("   Run: python backend/documents/download_hindi_font.py")
    return 'Helvetica', 'Helvetica-Bold'

HINDI_FONT, HINDI_FONT_BOLD = register_hindi_font()


def replace_rupee_symbol(text):
    """Replace rupee symbol (₹) with 'Rs.' for PDF compatibility"""
    if isinstance(text, str):
        text = re.sub(r'₹', 'Rs.', text)
        text = re.sub(r'Rs\.(\d)', r'Rs. \1', text)
    return text


def create_header_footer(canvas, doc, title):
    """Add header and footer to each page"""
    canvas.saveState()
    
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
    
    canvas.setFont('Helvetica', 8)
    canvas.drawString(72, 30, "www.sunnationalbank.in | 1800-123-4567 | investments@sunnationalbank.in")
    canvas.drawRightString(A4[0] - 72, 30, f"Page {doc.page}")
    
    canvas.restoreState()


def create_ppf_doc():
    """Create comprehensive Public Provident Fund (PPF) documentation in Hindi"""
    output_path = Path(__file__).parent / "investment_schemes_hindi" / "ppf_scheme_guide.pdf"
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
    
    story.append(Paragraph("पब्लिक प्रोविडेंट फंड (PPF)", title_style))
    story.append(Paragraph("दीर्घकालिक कर-बचत निवेश योजना", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("योजना अवलोकन", heading_style))
    overview_text = """
    पब्लिक प्रोविडेंट फंड (PPF) भारत सरकार द्वारा समर्थित एक दीर्घकालिक बचत योजना है। 
    यह आकर्षक ब्याज दरें, कर लाभ और पूर्ण पूंजी सुरक्षा प्रदान करती है। 
    PPF सेवानिवृत्ति योजना और दीर्घकालिक धन निर्माण के लिए एक सुरक्षित, कर-कुशल निवेश विकल्प चाहने वाले व्यक्तियों के लिए आदर्श है।
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
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("7.1% प्रति वर्ष (वार्षिक रूप से चक्रवृद्धि)<br/>सरकार द्वारा त्रैमासिक समीक्षा", table_cell_style)],
        [Paragraph("निवेश राशि", table_cell_style), Paragraph("न्यूनतम: Rs. 500 प्रति वर्ष<br/>अधिकतम: Rs. 1.5 लाख प्रति वर्ष", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("खाता खोलने की तारीख से 15 वर्ष<br/>5 वर्ष के ब्लॉक में विस्तारित किया जा सकता है", table_cell_style)],
        [Paragraph("कर लाभ", table_cell_style), Paragraph("Section 80C: Rs. 1.5 लाख तक कटौती<br/>अर्जित ब्याज पूरी तरह से कर-मुक्त<br/>परिपक्वता राशि कर-मुक्त", table_cell_style)],
        [Paragraph("निकासी", table_cell_style), Paragraph("7 वर्ष बाद आंशिक निकासी की अनुमति<br/>3वें से 6वें वर्ष तक ऋण सुविधा उपलब्ध", table_cell_style)],
        [Paragraph("जोखिम प्रोफ़ाइल", table_cell_style), Paragraph("शून्य जोखिम - सरकार द्वारा गारंटीकृत<br/>पूंजी सुरक्षा सुनिश्चित", table_cell_style)],
        [Paragraph("चक्रवृद्धि", table_cell_style), Paragraph("ब्याज वार्षिक रूप से चक्रवृद्धि<br/>महीने के 5वें और अंतिम दिन के बीच सबसे कम शेष राशि पर गणना", table_cell_style)],
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
    
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility = [
        "• <b>आयु:</b> कोई भी व्यक्ति (भारतीय निवासी) PPF खाता खोल सकता है",
        "• <b>खातों की संख्या:</b> प्रति व्यक्ति केवल एक PPF खाता",
        "• <b>HUF:</b> हिंदू अविभाजित परिवार PPF खाता नहीं खोल सकता",
        "• <b>NRI:</b> NRI नया PPF खाता नहीं खोल सकते (मौजूदा खाते बनाए रखे जा सकते हैं)",
        "• <b>नाबालिग:</b> माता-पिता/अभिभावक नाबालिग की ओर से PPF खाता खोल सकते हैं",
        "• <b>दस्तावेज:</b> PAN कार्ड, आधार कार्ड, पता प्रमाण और फोटो आवश्यक",
    ]
    for item in eligibility:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("निवेश विकल्प", heading_style))
    investment_info = """
    आप निम्नलिखित तरीकों से PPF में निवेश कर सकते हैं:
    """
    story.append(Paragraph(investment_info, normal_style))
    
    investment_options = [
        "• <b>एकमुश्त:</b> एक बार में पूरी राशि (Rs. 1.5 लाख तक) निवेश करें",
        "• <b>मासिक किस्त:</b> 12 महीनों में निवेश फैलाएं (न्यूनतम Rs. 500/वर्ष)",
        "• <b>आवृत्ति:</b> प्रति वर्ष अधिकतम 12 जमा",
        "• <b>भुगतान विधियां:</b> नकद, चेक, ऑनलाइन ट्रांसफर, या ऑटो-डेबिट सुविधा",
        "• <b>समय:</b> उस महीने के लिए ब्याज अर्जित करने के लिए महीने की 5 तारीख से पहले जमा करें",
    ]
    for option in investment_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("परिपक्वता और विस्तार", heading_style))
    maturity_info = [
        "• <b>परिपक्वता अवधि:</b> खाता खोलने की तारीख से 15 वर्ष",
        "• <b>विस्तार:</b> एक बार में 5 वर्ष के लिए विस्तारित किया जा सकता है (विस्तार पर कोई सीमा नहीं)",
        "• <b>विस्तार विकल्प:</b>",
        "  - योगदान के साथ जारी रखें (Rs. 1.5 लाख/वर्ष तक)",
        "  - योगदान के बिना जारी रखें (केवल ब्याज अर्जित होता है)",
        "• <b>परिपक्वता राशि:</b> पूरी तरह से या आंशिक रूप से निकाली जा सकती है",
        "• <b>आंशिक निकासी:</b> परिपक्वता के बाद, आंशिक राशि निकाली जा सकती है",
    ]
    for info in maturity_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("निकासी नियम", heading_style))
    withdrawal_header_style = ParagraphStyle('WithdrawalHeader', parent=styles['Normal'],
                                            fontSize=9, fontName=HINDI_FONT_BOLD,
                                            textColor=colors.whitesmoke, alignment=TA_LEFT)
    withdrawal_cell_style = ParagraphStyle('WithdrawalCell', parent=styles['Normal'],
                                           fontSize=8, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    withdrawal_rules = [
        [Paragraph("प्रकार", withdrawal_header_style), Paragraph("पात्रता", withdrawal_header_style), Paragraph("राशि", withdrawal_header_style), Paragraph("आवृत्ति", withdrawal_header_style)],
        [Paragraph("आंशिक निकासी", withdrawal_cell_style), Paragraph("7 वर्ष बाद", withdrawal_cell_style), Paragraph("निकासी के वर्ष से पहले 4वें वर्ष के अंत में शेष राशि का 50% तक", withdrawal_cell_style), Paragraph("प्रति वर्ष एक बार", withdrawal_cell_style)],
        [Paragraph("ऋण सुविधा", withdrawal_cell_style), Paragraph("3वें से 6वें वर्ष", withdrawal_cell_style), Paragraph("ऋण के वर्ष से पहले 2वें वर्ष के अंत में शेष राशि का 25% तक", withdrawal_cell_style), Paragraph("प्रति वर्ष एक बार", withdrawal_cell_style)],
        [Paragraph("समय से पहले बंद", withdrawal_cell_style), Paragraph("केवल जीवन-घातक बीमारी या मृत्यु के मामले में", withdrawal_cell_style), Paragraph("ब्याज के साथ पूरी राशि", withdrawal_cell_style), Paragraph("एक बार", withdrawal_cell_style)],
    ]
    
    withdrawal_table = Table(withdrawal_rules, colWidths=[1.5*inch, 1.5*inch, 1.8*inch, 1.2*inch])
    withdrawal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(withdrawal_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("कर लाभ (Section 80C)", heading_style))
    tax_benefits = [
        "• <b>निवेश कटौती:</b> प्रति वर्ष Rs. 1.5 लाख तक के योगदान Section 80C के तहत कटौती के लिए योग्य हैं",
        "• <b>ब्याज कर-मुक्त:</b> PPF पर अर्जित ब्याज आयकर से पूरी तरह से मुक्त है",
        "• <b>परिपक्वता कर-मुक्त:</b> पूरी परिपक्वता राशि (मूलधन + ब्याज) कर-मुक्त है",
        "• <b>EEE स्थिति:</b> PPF Exempt-Exempt-Exempt (EEE) स्थिति का आनंद लेता है - निवेश, ब्याज और परिपक्वता सभी कर-मुक्त",
        "• <b>कोई TDS नहीं:</b> ब्याज या परिपक्वता राशि पर स्रोत पर कर कटौती नहीं",
        "• <b>धन कर:</b> PPF शेष राशि धन कर से मुक्त है",
    ]
    for benefit in tax_benefits:
        story.append(Paragraph(benefit, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("परिपक्वता गणना उदाहरण", heading_style))
    maturity_header_style = ParagraphStyle('MaturityHeader', parent=styles['Normal'],
                                          fontSize=8, fontName=HINDI_FONT_BOLD,
                                          textColor=colors.whitesmoke, alignment=TA_CENTER)
    maturity_cell_style = ParagraphStyle('MaturityCell', parent=styles['Normal'],
                                        fontSize=7, fontName=HINDI_FONT,
                                        alignment=TA_CENTER)
    
    maturity_examples = [
        [Paragraph("वार्षिक निवेश", maturity_header_style), Paragraph("अवधि", maturity_header_style), Paragraph("कुल निवेश", maturity_header_style), Paragraph("परिपक्वता राशि (लगभग)", maturity_header_style), Paragraph("रिटर्न", maturity_header_style)],
        [Paragraph("Rs. 1,00,000", maturity_cell_style), Paragraph("15 वर्ष", maturity_cell_style), Paragraph("Rs. 15,00,000", maturity_cell_style), Paragraph("Rs. 31,00,000", maturity_cell_style), Paragraph("Rs. 16,00,000", maturity_cell_style)],
        [Paragraph("Rs. 1,50,000", maturity_cell_style), Paragraph("15 वर्ष", maturity_cell_style), Paragraph("Rs. 22,50,000", maturity_cell_style), Paragraph("Rs. 46,50,000", maturity_cell_style), Paragraph("Rs. 24,00,000", maturity_cell_style)],
        [Paragraph("Rs. 50,000", maturity_cell_style), Paragraph("15 वर्ष", maturity_cell_style), Paragraph("Rs. 7,50,000", maturity_cell_style), Paragraph("Rs. 15,50,000", maturity_cell_style), Paragraph("Rs. 8,00,000", maturity_cell_style)],
    ]
    
    maturity_table = Table(maturity_examples, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1.5*inch, 1.1*inch])
    maturity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(maturity_table)
    story.append(Paragraph("<i>नोट: परिपक्वता राशियां वर्तमान ब्याज दर 7.1% प्रति वर्ष के आधार पर अनुमानित हैं।</i>", normal_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("खाता खोलने की प्रक्रिया", heading_style))
    process_steps = [
        ("<b>चरण 1: शाखा पर जाएं</b>", "आवश्यक दस्तावेजों के साथ किसी भी सन नेशनल बैंक शाखा पर जाएं।"),
        ("<b>चरण 2: फॉर्म भरें</b>", "PPF खाता खोलने का फॉर्म (फॉर्म A) और नामांकन फॉर्म भरें।"),
        ("<b>चरण 3: दस्तावेज जमा करें</b>", "KYC दस्तावेज (PAN, आधार, पता प्रमाण) और फोटो जमा करें।"),
        ("<b>चरण 4: प्रारंभिक जमा</b>", "नकद, चेक, या ऑनलाइन ट्रांसफर के माध्यम से प्रारंभिक जमा करें (न्यूनतम Rs. 500)।"),
        ("<b>चरण 5: खाता सक्रियण</b>", "खाता सक्रिय हो जाता है और PPF पासबुक/स्टेटमेंट जारी किया जाता है।"),
        ("<b>चरण 6: ऑनलाइन पहुंच</b>", "PPF खाते को ऑनलाइन प्रबंधित करने के लिए इंटरनेट बैंकिंग के लिए पंजीकरण करें।"),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: क्या मेरे पास कई PPF खाते हो सकते हैं?</b>",
         "नहीं, प्रति व्यक्ति केवल एक PPF खाता अनुमत है। कई खाते खोलने से जुर्माना और बंद हो सकता है।"),
        
        ("<b>Q2: यदि मैं एक वर्ष का योगदान चूक जाऊं तो क्या होगा?</b>",
         "योगदान चूकने से खाता बंद नहीं होता है, लेकिन आप उस वर्ष का कर लाभ खो देते हैं। खाता ब्याज अर्जित करना जारी रखता है।"),
        
        ("<b>Q3: क्या मैं अपना PPF खाता स्थानांतरित कर सकता हूं?</b>",
         "हां, PPF खाता एक बैंक/डाकघर से दूसरे में स्थानांतरित किया जा सकता है। फॉर्म H जमा करना होगा।"),
        
        ("<b>Q4: क्या PPF FD से बेहतर है?</b>",
         "PPF कर लाभ प्रदान करता है (80C कटौती + कर-मुक्त ब्याज) और चक्रवृद्धि के कारण उच्च प्रभावी रिटर्न, जो दीर्घकालिक कर-बचत के लिए इसे बेहतर बनाता है।"),
        
        ("<b>Q5: क्या मैं PPF के खिलाफ ऋण ले सकता हूं?</b>",
         "हां, 3वें से 6वें वर्ष तक ऋण सुविधा उपलब्ध है। ऋण राशि ऋण के वर्ष से पहले 2वें वर्ष के अंत में शेष राशि का 25% तक है।"),
        
        ("<b>Q6: ब्याज गणना विधि क्या है?</b>",
         "ब्याज की गणना प्रत्येक महीने के 5वें और अंतिम दिन के बीच सबसे कम शेष राशि पर की जाती है। ब्याज वार्षिक रूप से 31 मार्च को जमा किया जाता है।"),
        
        ("<b>Q7: क्या मैं 15 वर्ष बाद PPF का विस्तार कर सकता हूं?</b>",
         "हां, आप PPF खाते को 5 वर्ष के ब्लॉक में अनिश्चित काल तक विस्तारित कर सकते हैं। आप योगदान के साथ या बिना जारी रखना चुन सकते हैं।"),
        
        ("<b>Q8: क्या PPF सुरक्षित है?</b>",
         "हां, PPF पूरी तरह से सुरक्षित है क्योंकि यह भारत सरकार द्वारा समर्थित है। पूंजी और रिटर्न गारंटीकृत हैं।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("महत्वपूर्ण नोट्स", heading_style))
    notes = [
        "• ब्याज दर सरकारी अधिसूचना के अनुसार बदल सकती है (त्रैमासिक समीक्षा)।",
        "• खाते को सक्रिय रखने के लिए प्रति वर्ष न्यूनतम Rs. 500 का एक जमा करना होगा।",
        "• नामांकन अनिवार्य है - खाता खोलने पर नामांकन फॉर्म भरना सुनिश्चित करें।",
        "• PPF खाता परिपक्वता से पहले जीवन-घातक बीमारी के मामले को छोड़कर बंद नहीं किया जा सकता है।",
        "• ब्याज दर पूरे वित्तीय वर्ष (अप्रैल से मार्च) के लिए निश्चित है।",
        "• PPF खाता नेट बैंकिंग के माध्यम से ऑनलाइन खोला जा सकता है (यदि योग्य है)।",
        "• सभी लेनदेन (जमा, निकासी) PPF पासबुक/स्टेटमेंट में दर्ज किए जाते हैं।",
        "• लंबी लॉक-इन अवधि और कर लाभों के कारण PPF सेवानिवृत्ति योजना के लिए आदर्श है।",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "PPF योजना गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "PPF योजना गाइड"))
    
    return output_path


def create_nps_doc():
    """Create comprehensive National Pension System (NPS) documentation in Hindi"""
    output_path = Path(__file__).parent / "investment_schemes_hindi" / "nps_scheme_guide.pdf"
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
    
    story.append(Paragraph("नेशनल पेंशन सिस्टम (NPS)", title_style))
    story.append(Paragraph("बाजार-लिंक्ड सेवानिवृत्ति बचत योजना", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("योजना अवलोकन", heading_style))
    overview_text = """
    नेशनल पेंशन सिस्टम (NPS) PFRDA (पेंशन फंड नियामक और विकास प्राधिकरण) द्वारा विनियमित एक स्वैच्छिक, परिभाषित योगदान सेवानिवृत्ति बचत योजना है। 
    NPS निवेश विकल्पों में लचीलापन और आकर्षक कर लाभों के साथ बाजार-लिंक्ड रिटर्न प्रदान करता है। 
    यह व्यवस्थित बचत के माध्यम से व्यक्तियों को सेवानिवृत्ति कोष बनाने में मदद करने के लिए डिज़ाइन किया गया है।
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
        [Paragraph("रिटर्न", table_cell_style), Paragraph("बाजार-लिंक्ड रिटर्न (आमतौर पर 8-12% प्रति वर्ष ऐतिहासिक रूप से)<br/>रिटर्न चुने गए परिसंपत्ति आवंटन पर निर्भर करता है", table_cell_style)],
        [Paragraph("निवेश राशि", table_cell_style), Paragraph("न्यूनतम: Rs. 500 प्रति योगदान<br/>न्यूनतम: Rs. 1,000 प्रति वर्ष<br/>कोई अधिकतम सीमा नहीं", table_cell_style)],
        [Paragraph("खाता प्रकार", table_cell_style), Paragraph("Tier-I (पेंशन खाता): अनिवार्य, कर लाभ<br/>Tier-II (बचत खाता): वैकल्पिक, कोई कर लाभ नहीं", table_cell_style)],
        [Paragraph("कर लाभ", table_cell_style), Paragraph("Tier-I: Rs. 1.5 लाख तक (80C) + Rs. 50,000 (80CCD(1B))<br/>Tier-II: कोई कर लाभ नहीं", table_cell_style)],
        [Paragraph("निकासी", table_cell_style), Paragraph("Tier-I: 60 वर्ष पर 60% निकासी (कर योग्य)<br/>40% को एन्युइटी खरीदने के लिए उपयोग करना होगा (कर-मुक्त)<br/>Tier-II: लचीली निकासी", table_cell_style)],
        [Paragraph("जोखिम प्रोफ़ाइल", table_cell_style), Paragraph("बाजार-लिंक्ड - रिटर्न परिसंपत्ति आवंटन के आधार पर भिन्न होता है<br/>इक्विटी एक्सपोजर 75% तक (50 वर्ष तक), 50% (50 वर्ष के बाद)", table_cell_style)],
        [Paragraph("पेंशन", table_cell_style), Paragraph("60% निकाला जा सकता है, 40% नियमित पेंशन के लिए एन्युइटी खरीदने के लिए उपयोग किया जाता है", table_cell_style)],
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
    
    story.append(Paragraph("पात्रता मानदंड", heading_style))
    eligibility = [
        "• <b>आयु:</b> 18 से 70 वर्ष (नया खाता खोलने के लिए)",
        "• <b>निवास:</b> भारतीय नागरिक (निवासी और NRI) NPS खाता खोल सकते हैं",
        "• <b>दस्तावेज:</b> PAN कार्ड (अनिवार्य), आधार कार्ड, पता प्रमाण और फोटो",
        "• <b>KYC:</b> पूर्ण KYC सत्यापन आवश्यक",
        "• <b>कई खाते:</b> प्रति व्यक्ति केवल एक NPS खाता (PRAN - स्थायी सेवानिवृत्ति खाता संख्या)",
    ]
    for item in eligibility:
        story.append(Paragraph(item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("निवेश विकल्प और परिसंपत्ति आवंटन", heading_style))
    story.append(Paragraph("<b>परिसंपत्ति वर्ग:</b>", subheading_style))
    asset_classes = [
        "• <b>इक्विटी (E):</b> स्टॉक में निवेश - उच्च जोखिम, उच्च रिटर्न क्षमता",
        "• <b>कॉर्पोरेट बॉन्ड (C):</b> कॉर्पोरेट ऋण में निवेश - मध्यम जोखिम",
        "• <b>सरकारी प्रतिभूतियां (G):</b> सरकारी बॉन्ड में निवेश - कम जोखिम",
        "• <b>वैकल्पिक निवेश फंड (A):</b> REITs, InvITs - 5% तक आवंटन",
    ]
    for asset in asset_classes:
        story.append(Paragraph(asset, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>निवेश विकल्प:</b>", subheading_style))
    choices = [
        "• <b>ऑटो चॉइस (लाइफसाइकल फंड):</b> आयु के आधार पर परिसंपत्ति आवंटन स्वचालित रूप से समायोजित",
        "• <b>एक्टिव चॉइस:</b> आप परिसंपत्ति आवंटन तय करते हैं (इक्विटी: 0-75% 50 वर्ष तक, 0-50% 50 वर्ष के बाद)",
        "• <b>डिफॉल्ट विकल्प:</b> यदि कोई विकल्प नहीं बनाया गया है, तो ऑटो चॉइस चुना जाता है",
    ]
    for choice in choices:
        story.append(Paragraph(choice, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("कर लाभ", heading_style))
    tax_info = [
        "• <b>Section 80C:</b> प्रति वर्ष Rs. 1.5 लाख तक के योगदान कटौती के लिए योग्य हैं (केवल Tier-I)",
        "• <b>Section 80CCD(1B):</b> प्रति वर्ष Rs. 50,000 की अतिरिक्त कटौती (80C सीमा के अतिरिक्त)",
        "• <b>नियोक्ता योगदान:</b> वेतन का 10% तक नियोक्ता योगदान कर-मुक्त है (80CCD(2))",
        "• <b>परिपक्वता:</b> एन्युइटी खरीदने के लिए उपयोग किए गए कोष का 40% कर-मुक्त है",
        "• <b>निकासी:</b> 60 वर्ष पर 60% निकासी आयकर स्लैब के अनुसार कर योग्य है",
        "• <b>समय से पहले निकासी:</b> 3 वर्ष बाद 20% निकासी की अनुमति (80% को एन्युइटी खरीदनी होगी)",
    ]
    for info in tax_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("निकासी नियम", heading_style))
    withdrawal_header_style = ParagraphStyle('WithdrawalHeader', parent=styles['Normal'],
                                            fontSize=8, fontName=HINDI_FONT_BOLD,
                                            textColor=colors.whitesmoke, alignment=TA_LEFT)
    withdrawal_cell_style = ParagraphStyle('WithdrawalCell', parent=styles['Normal'],
                                           fontSize=7, fontName=HINDI_FONT,
                                           alignment=TA_LEFT)
    
    withdrawal_rules = [
        [Paragraph("परिदृश्य", withdrawal_header_style), Paragraph("निकासी राशि", withdrawal_header_style), Paragraph("एन्युइटी आवश्यकता", withdrawal_header_style), Paragraph("कर उपचार", withdrawal_header_style)],
        [Paragraph("60 वर्ष पर (सामान्य)", withdrawal_cell_style), Paragraph("कोष का 60%", withdrawal_cell_style), Paragraph("40% को एन्युइटी खरीदनी होगी", withdrawal_cell_style), Paragraph("60% कर योग्य, एन्युइटी कर-मुक्त", withdrawal_cell_style)],
        [Paragraph("समय से पहले (3 वर्ष बाद)", withdrawal_cell_style), Paragraph("कोष का 20%", withdrawal_cell_style), Paragraph("80% को एन्युइटी खरीदनी होगी", withdrawal_cell_style), Paragraph("20% कर योग्य, एन्युइटी कर-मुक्त", withdrawal_cell_style)],
        [Paragraph("मृत्यु", withdrawal_cell_style), Paragraph("नामांकित व्यक्ति को 100%", withdrawal_cell_style), Paragraph("कोई एन्युइटी आवश्यक नहीं", withdrawal_cell_style), Paragraph("नामांकित व्यक्ति के लिए कर-मुक्त", withdrawal_cell_style)],
        [Paragraph("Tier-II खाता", withdrawal_cell_style), Paragraph("कभी भी 100%", withdrawal_cell_style), Paragraph("कोई एन्युइटी आवश्यक नहीं", withdrawal_cell_style), Paragraph("कोई कर लाभ नहीं", withdrawal_cell_style)],
    ]
    
    withdrawal_table = Table(withdrawal_rules, colWidths=[1.5*inch, 1.3*inch, 1.5*inch, 1.7*inch])
    withdrawal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(withdrawal_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("खाता खोलने की प्रक्रिया", heading_style))
    process_steps = [
        ("<b>चरण 1: POP चुनें</b>", "पॉइंट ऑफ प्रेजेंस (POP) चुनें - सन नेशनल बैंक शाखा या ऑनलाइन।"),
        ("<b>चरण 2: फॉर्म भरें</b>", "NPS खाता खोलने का फॉर्म (फॉर्म CS-S1) व्यक्तिगत विवरण के साथ भरें।"),
        ("<b>चरण 3: दस्तावेज जमा करें</b>", "KYC दस्तावेज जमा करें (PAN अनिवार्य, आधार, पता प्रमाण, फोटो)।"),
        ("<b>चरण 4: योजना चुनें</b>", "ऑटो चॉइस या एक्टिव चॉइस और परिसंपत्ति आवंटन चुनें।"),
        ("<b>चरण 5: प्रारंभिक योगदान</b>", "प्रारंभिक योगदान करें (Tier-I के लिए न्यूनतम Rs. 500)।"),
        ("<b>चरण 6: PRAN जनरेशन</b>", "PRAN (स्थायी सेवानिवृत्ति खाता संख्या) जेनरेट किया जाता है और आपको भेजा जाता है।"),
        ("<b>चरण 7: ऑनलाइन पहुंच</b>", "खाता प्रबंधन के लिए PRAN और OTP का उपयोग करके ऑनलाइन पहुंच सक्रिय करें।"),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("अक्सर पूछे जाने वाले प्रश्न", heading_style))
    faqs = [
        ("<b>Q1: Tier-I और Tier-II के बीच क्या अंतर है?</b>",
         "Tier-I अनिवार्य पेंशन खाता है जिसमें कर लाभ हैं लेकिन निकासी प्रतिबंध हैं। Tier-II वैकल्पिक बचत खाता है जिसमें कोई कर लाभ नहीं है लेकिन लचीली निकासी है।"),
        
        ("<b>Q2: क्या मैं अपना परिसंपत्ति आवंटन बदल सकता हूं?</b>",
         "हां, आप प्रति वित्तीय वर्ष दो बार परिसंपत्ति आवंटन बदल सकते हैं। परिवर्तन ऑनलाइन या POP के माध्यम से किए जा सकते हैं।"),
        
        ("<b>Q3: यदि मैं नियमित रूप से योगदान नहीं करता हूं तो क्या होगा?</b>",
         "खाता सक्रिय रहता है। योगदान चूकने के लिए कोई जुर्माना नहीं है, लेकिन आप उस वर्ष का कर लाभ खो देते हैं।"),
        
        ("<b>Q4: क्या मैं 60 वर्ष से पहले निकासी कर सकता हूं?</b>",
         "हां, 3 वर्ष बाद, आप कोष का 20% तक निकाल सकते हैं। शेष 80% को एन्युइटी खरीदने के लिए उपयोग करना होगा।"),
        
        ("<b>Q5: क्या NPS PPF से बेहतर है?</b>",
         "NPS संभावित रूप से उच्च रिटर्न (बाजार-लिंक्ड) और अतिरिक्त Rs. 50,000 कर कटौती प्रदान करता है, लेकिन बाजार जोखिम है। PPF निश्चित रिटर्न के साथ सुरक्षित है।"),
        
        ("<b>Q6: एन्युइटी क्या है?</b>",
         "एन्युइटी बीमा कंपनियों से खरीदा गया एक पेंशन उत्पाद है। यह सेवानिवृत्ति के बाद नियमित मासिक/त्रैमासिक पेंशन भुगतान प्रदान करता है।"),
        
        ("<b>Q7: क्या मेरे पास कई NPS खाते हो सकते हैं?</b>",
         "नहीं, प्रति व्यक्ति केवल एक NPS खाता। PRAN अद्वितीय है और PAN से जुड़ा हुआ है।"),
        
        ("<b>Q8: शुल्क क्या हैं?</b>",
         "खाता खोलना: Rs. 200 (एक बार), वार्षिक रखरखाव: Rs. 95, लेनदेन शुल्क: Rs. 3.75 प्रति योगदान, फंड प्रबंधन: AUM का 0.01%।"),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("महत्वपूर्ण नोट्स", heading_style))
    notes = [
        "• NPS रिटर्न बाजार-लिंक्ड हैं और गारंटीकृत नहीं हैं - रिटर्न बाजार की स्थितियों के आधार पर भिन्न हो सकते हैं।",
        "• 50 वर्ष के बाद जोखिम प्रबंधन के लिए इक्विटी आवंटन स्वचालित रूप से कम हो जाता है।",
        "• PRAN पोर्टेबल है - सभी POPs और फंड मैनेजरों में उपयोग किया जा सकता है।",
        "• नामांकन अनिवार्य है - नामांकन विवरण अपडेट किए गए हैं यह सुनिश्चित करें।",
        "• NPS खाता विशिष्ट परिस्थितियों को छोड़कर 60 वर्ष से पहले बंद नहीं किया जा सकता है।",
        "• नियमित योगदान चक्रवृद्धि के माध्यम से एक पर्याप्त सेवानिवृत्ति कोष बनाने में मदद करते हैं।",
        "• आयु और जोखिम भूख के आधार पर समय-समय पर पोर्टफोलियो की समीक्षा और पुनर्संतुलन करें।",
        "• कर लाभों और दीर्घकालिक धन निर्माण के कारण NPS सेवानिवृत्ति योजना के लिए आदर्श है।",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "NPS योजना गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "NPS योजना गाइड"))
    
    return output_path


def create_ssy_doc():
    """Create comprehensive Sukanya Samriddhi Yojana (SSY) documentation in Hindi"""
    output_path = Path(__file__).parent / "investment_schemes_hindi" / "ssy_scheme_guide.pdf"
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
    
    story.append(Paragraph("सुकन्या समृद्धि योजना (SSY)", title_style))
    story.append(Paragraph("बालिका बचत योजना - सरकार द्वारा समर्थित", subheading_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("योजना अवलोकन", heading_style))
    overview_text = """
    सुकन्या समृद्धि योजना (SSY) भारत सरकार द्वारा विशेष रूप से बालिकाओं के लाभ के लिए शुरू की गई एक छोटी बचत योजना है। 
    यह छोटी बचत योजनाओं में सबसे अधिक ब्याज दरों में से एक प्रदान करती है और आकर्षक कर लाभ प्रदान करती है। 
    यह योजना बालिकाओं की शिक्षा और विवाह खर्चों के लिए उनके वित्तीय भविष्य को सुरक्षित करने का लक्ष्य रखती है।
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
        [Paragraph("ब्याज दर", table_cell_style), Paragraph("8.2% प्रति वर्ष (वार्षिक रूप से चक्रवृद्धि)<br/>छोटी बचत योजनाओं में सबसे अधिक दरों में से एक", table_cell_style)],
        [Paragraph("निवेश राशि", table_cell_style), Paragraph("न्यूनतम: Rs. 250 प्रति वर्ष<br/>अधिकतम: Rs. 1.5 लाख प्रति वर्ष", table_cell_style)],
        [Paragraph("अवधि", table_cell_style), Paragraph("खाता खोलने से 21 वर्ष<br/>या जब तक बालिका 21 वर्ष की नहीं हो जाती, जो भी बाद में हो", table_cell_style)],
        [Paragraph("पात्रता", table_cell_style), Paragraph("10 वर्ष से कम उम्र की बालिका<br/>प्रति बालिका केवल एक खाता", table_cell_style)],
        [Paragraph("कर लाभ", table_cell_style), Paragraph("Section 80C: Rs. 1.5 लाख तक कटौती<br/>ब्याज और परिपक्वता राशि पूरी तरह से कर-मुक्त", table_cell_style)],
        [Paragraph("निकासी", table_cell_style), Paragraph("बालिका के 18 वर्ष होने के बाद 50% निकासी की अनुमति<br/>शिक्षा/विवाह खर्चों के लिए", table_cell_style)],
        [Paragraph("जोखिम प्रोफ़ाइल", table_cell_style), Paragraph("शून्य जोखिम - सरकार द्वारा गारंटीकृत<br/>पूर्ण पूंजी सुरक्षा", table_cell_style)],
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
    story.append(Paragraph("पात्रता", heading_style))
    eligibility = [
        "• <b>बालिका:</b> खाता खोलने के समय 10 वर्ष से कम उम्र होनी चाहिए",
        "• <b>खाता धारक:</b> माता-पिता या कानूनी अभिभावक खाता खोल सकते हैं",
        "• <b>खातों की संख्या:</b> प्रति परिवार अधिकतम 2 खाते (2 बालिकाओं के लिए)",
        "• <b>दस्तावेज:</b> बालिका का जन्म प्रमाणपत्र, माता-पिता के KYC दस्तावेज, फोटो",
    ]
    for item in eligibility:
        story.append(Paragraph(item, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("निकासी नियम", heading_style))
    withdrawal_info = [
        "• <b>18 वर्ष के बाद:</b> उच्च शिक्षा खर्चों के लिए शेष राशि का 50% निकाला जा सकता है",
        "• <b>विवाह:</b> यदि बालिका 18 वर्ष के बाद विवाह करती है तो खाता बंद किया जा सकता है",
        "• <b>परिपक्वता:</b> खाता खोलने से 21 वर्ष बाद या जब बालिका 21 वर्ष की हो जाती है तो परिपक्व होता है",
        "• <b>समय से पहले बंद:</b> केवल खाता धारक या बालिका की मृत्यु के मामले में अनुमति",
    ]
    for info in withdrawal_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("कर लाभ", heading_style))
    tax_info = [
        "• <b>Section 80C:</b> प्रति वर्ष Rs. 1.5 लाख तक के योगदान कटौती के लिए योग्य हैं",
        "• <b>ब्याज:</b> अर्जित ब्याज पूरी तरह से कर-मुक्त है",
        "• <b>परिपक्वता:</b> पूरी परिपक्वता राशि कर-मुक्त है",
        "• <b>EEE स्थिति:</b> निवेश, ब्याज और परिपक्वता सभी कर-मुक्त",
    ]
    for info in tax_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("महत्वपूर्ण नोट्स", heading_style))
    notes = [
        "• खाता बालिका के 10 वर्ष की होने से पहले खोला जाना चाहिए।",
        "• खाते को सक्रिय रखने के लिए प्रति वर्ष न्यूनतम Rs. 250 का एक जमा करना होगा।",
        "• ब्याज दर की सरकार द्वारा त्रैमासिक समीक्षा की जाती है।",
        "• खाता एक बैंक/डाकघर से दूसरे में स्थानांतरित किया जा सकता है।",
        "• नामांकन अनिवार्य है।",
    ]
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "SSY योजना गाइड"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "SSY योजना गाइड"))
    
    return output_path


if __name__ == "__main__":
    print("सन नेशनल बैंक के लिए हिंदी में व्यापक निवेश योजना दस्तावेज बनाना...")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "investment_schemes_hindi"
    output_dir.mkdir(exist_ok=True)
    
    docs_created = []
    
    print("\n1️⃣  PPF योजना गाइड बनाना...")
    ppf_path = create_ppf_doc()
    docs_created.append(("PPF", ppf_path))
    print(f"   ✓ बनाया गया: {ppf_path.name}")
    
    print("\n2️⃣  NPS योजना गाइड बनाना...")
    nps_path = create_nps_doc()
    docs_created.append(("NPS", nps_path))
    print(f"   ✓ बनाया गया: {nps_path.name}")
    
    print("\n3️⃣  SSY योजना गाइड बनाना...")
    ssy_path = create_ssy_doc()
    docs_created.append(("SSY", ssy_path))
    print(f"   ✓ बनाया गया: {ssy_path.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ सफलतापूर्वक {len(docs_created)} व्यापक निवेश योजना गाइड बनाए गए!")
    print(f"📁 स्थान: {output_dir}")

