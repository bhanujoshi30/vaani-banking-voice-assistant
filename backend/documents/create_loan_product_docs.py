"""
Create Comprehensive Loan Product Documentation for RAG
These PDFs contain detailed information about each loan type offered by Sun National Bank
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from pathlib import Path
import re


def replace_rupee_symbol(text):
    """
    Replace rupee symbol (Rs.) with 'Rs.' for PDF compatibility
    ReportLab's default fonts don't support Unicode rupee symbol properly
    """
    if isinstance(text, str):
        # Replace Rs. with Rs. (with proper spacing)
        text = re.sub(r'Rs.(\d)', r'Rs. \1', text)
        text = re.sub(r'Rs.', 'Rs.', text)
        # Handle cases like "Rs. 5 lakhs" -> "Rs. 5 lakhs"
        text = re.sub(r'Rs\.(\d)', r'Rs. \1', text)
    return text


def create_header_footer(canvas, doc, title):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFillColor(colors.HexColor('#FF8F42'))
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(72, A4[1] - 50, "SUN NATIONAL BANK")
    
    canvas.setFillColor(colors.black)
    canvas.setFont('Helvetica', 10)
    canvas.drawString(72, A4[1] - 65, title)
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawString(72, 30, "www.sunnationalbank.in | 1800-123-4567 | loans@sunnationalbank.in")
    canvas.drawRightString(A4[0] - 72, 30, f"Page {doc.page}")
    
    canvas.restoreState()


def create_home_loan_doc():
    """Create comprehensive Home Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "home_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6)
    
    # Title
    story.append(Paragraph("HOME LOAN", title_style))
    story.append(Paragraph("Complete Product Guide & Information", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """
    Sun National Bank's Home Loan is designed to help you achieve your dream of owning a home. 
    Whether you're buying a new property, constructing a house, or renovating your existing home, 
    we offer flexible financing options with competitive interest rates and convenient repayment terms.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("KEY FEATURES", heading_style))
    features = [
        ["Feature", "Details"],
        ["Loan Amount", replace_rupee_symbol("Rs. 5 lakhs to Rs. 5 crores")],
        ["Interest Rate", "8.35% - 9.50% p.a. (Floating Rate)\n8.85% - 10.00% p.a. (Fixed Rate)"],
        ["Tenure", "Up to 30 years (maximum age at maturity: 70 years)"],
        ["Processing Fee", replace_rupee_symbol("0.50% of loan amount (Min: Rs. 5,000, Max: Rs. 25,000) + GST")],
        ["Prepayment Charges", "Nil for floating rate loans\n2% + GST for fixed rate loans"],
        ["Loan-to-Value Ratio", replace_rupee_symbol("Up to 90% for loans up to Rs. 30 lakhs\nUp to 80% for loans above Rs. 30 lakhs")],
        ["Moratorium Period", "Up to 48 months for under-construction properties"],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Types of Home Loans
    story.append(Paragraph("TYPES OF HOME LOANS", heading_style))
    
    story.append(Paragraph("1. Home Purchase Loan", subheading_style))
    story.append(Paragraph("Finance for purchasing a ready-to-move-in residential property (new or resale).", normal_style))
    
    story.append(Paragraph("2. Home Construction Loan", subheading_style))
    story.append(Paragraph("Finance for constructing a house on a plot of land that you already own. Disbursement is done in stages based on construction progress.", normal_style))
    
    story.append(Paragraph("3. Plot + Construction Loan", subheading_style))
    story.append(Paragraph("Combined financing for purchasing a plot and constructing a house on it.", normal_style))
    
    story.append(Paragraph("4. Home Extension Loan", subheading_style))
    story.append(Paragraph("Finance for extending or expanding your existing residential property.", normal_style))
    
    story.append(Paragraph("5. Home Renovation Loan", subheading_style))
    story.append(Paragraph("Finance for renovating, repairing, or improving your existing home. Maximum loan amount: Rs. 50 lakhs.", normal_style))
    
    story.append(Paragraph("6. Balance Transfer Loan", subheading_style))
    story.append(Paragraph("Transfer your existing home loan from another bank to Sun National Bank to avail better interest rates or additional top-up loan.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility Criteria
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    
    eligibility = [
        ["Criteria", "Salaried Individuals", "Self-Employed"],
        ["Age", "21 - 65 years", "25 - 70 years"],
        ["Minimum Income", "Rs. 25,000 per month", "Rs. 3,00,000 per annum"],
        ["Work Experience", "Minimum 2 years (1 year in current organization)", "Minimum 3 years in business"],
        ["Credit Score", "Minimum 700 (CIBIL)", "Minimum 700 (CIBIL)"],
        ["Employment Type", "Permanent employee with reputed organization", "Stable business with ITR filed for last 3 years"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    
    story.append(Paragraph("For Salaried Applicants:", subheading_style))
    salaried_docs = [
        "• Completed loan application form with photograph",
        "• Identity Proof: PAN Card, Aadhaar Card, Passport, Voter ID, or Driving License",
        "• Address Proof: Aadhaar Card, Passport, Utility Bills, or Rent Agreement",
        "• Age Proof: Birth Certificate, PAN Card, or Passport",
        "• Income Proof: Last 6 months' salary slips and bank statements",
        "• Form 16 or IT Returns for last 2 years",
        "• Employment Proof: Employment letter or contract",
        "• Property Documents: Sale deed, approved building plan, NOC from society",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("For Self-Employed Applicants:", subheading_style))
    self_emp_docs = [
        "• All documents listed above for salaried individuals",
        "• Business Proof: Business registration certificate, GST registration, Partnership deed",
        "• Income Tax Returns for last 3 years with computation of income",
        "• Audited Balance Sheet and Profit & Loss statements for last 3 years",
        "• Bank statements for last 12 months (business account)",
        "• List of existing business loans with repayment track record",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # EMI Calculation Example
    story.append(Paragraph("EMI CALCULATION EXAMPLES", heading_style))
    emi_examples_text = """
    The EMI (Equated Monthly Installment) is calculated using the formula:<br/>
    <b>EMI = [P x R x (1+R)^N] / [(1+R)^N-1]</b><br/>
    Where: P = Principal loan amount, R = Monthly interest rate, N = Number of months
    """
    story.append(Paragraph(emi_examples_text, normal_style))
    
    emi_data = [
        ["Loan Amount", "Interest Rate", "Tenure", "Monthly EMI", "Total Interest", "Total Payment"],
        ["Rs. 25,00,000", "8.50% p.a.", "20 years", "Rs. 21,612", "Rs. 26,86,880", "Rs. 51,86,880"],
        ["Rs. 50,00,000", "8.50% p.a.", "25 years", "Rs. 39,712", "Rs. 69,13,600", "Rs. 1,19,13,600"],
        ["Rs. 75,00,000", "9.00% p.a.", "30 years", "Rs. 60,347", "Rs. 1,42,24,920", "Rs. 2,17,24,920"],
        ["Rs. 1,00,00,000", "9.00% p.a.", "20 years", "Rs. 89,973", "Rs. 1,15,93,520", "Rs. 2,15,93,520"],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Special Benefits
    story.append(Paragraph("SPECIAL BENEFITS & OFFERS", heading_style))
    benefits = [
        "• <b>Women Borrowers:</b> 0.05% concession in interest rate for women applicants",
        "• <b>No Hidden Charges:</b> Complete transparency in all fees and charges",
        "• <b>Quick Approval:</b> In-principle approval within 48 hours",
        "• <b>Flexible Repayment:</b> Option to increase EMI as income grows (Step-up EMI)",
        "• <b>Tax Benefits:</b> Deduction up to Rs. 1.5 lakhs on principal (Sec 80C) + Rs. 2 lakhs on interest (Sec 24)",
        "• <b>Free Insurance:</b> Complimentary property insurance for first year",
        "• <b>Doorstep Service:</b> Documentation pickup and delivery at your convenience",
        "• <b>Digital Process:</b> Paperless loan application through mobile app or website",
    ]
    for benefit in benefits:
        story.append(Paragraph(benefit, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Fees and Charges
    story.append(Paragraph("FEES AND CHARGES", heading_style))
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "0.50% of loan amount (Min Rs. 5,000, Max Rs. 25,000) + GST"],
        ["Login Fee/Documentation Charges", "Rs. 5,000 + GST (One-time)"],
        ["Property Valuation Charges", "Actual cost (Rs. 3,000 - Rs. 10,000 depending on property)"],
        ["Legal & Technical Charges", "Rs. 5,000 - Rs. 15,000 + GST"],
        ["Stamp Duty & Registration", "As per state government norms (customer's account)"],
        ["Late Payment Penalty", "2% per month on overdue amount"],
        ["Cheque/NACH Bounce Charges", "Rs. 500 per instance"],
        ["Part Prepayment Charges (Floating)", "Nil"],
        ["Part Prepayment Charges (Fixed)", "2% of prepaid amount + GST"],
        ["Foreclosure Charges (Floating)", "Nil"],
        ["Foreclosure Charges (Fixed)", "3% of outstanding principal + GST"],
        ["Loan Cancellation Charges", "Rs. 5,000 + GST (if cancelled after approval)"],
        ["Duplicate Statement Charges", "Rs. 250 per statement"],
        ["NOC/Closure Certificate", "Rs. 1,000 + GST"],
        ["Swap Charges (Fixed to Floating)", "0.50% of outstanding principal + GST"],
    ]
    
    fees_table = Table(fees_data, colWidths=[3.5*inch, 3*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    # Loan Process
    story.append(Paragraph("LOAN APPLICATION PROCESS", heading_style))
    
    process_steps = [
        ("<b>Step 1: Application</b>", "Submit loan application online or visit nearest branch. Provide basic details and upload documents."),
        ("<b>Step 2: Document Verification</b>", "Our team verifies your documents and conducts income assessment. Usually completed within 2 working days."),
        ("<b>Step 3: Property Evaluation</b>", "Technical and legal verification of the property is conducted by our empaneled valuers."),
        ("<b>Step 4: Credit Assessment</b>", "Your credit history, repayment capacity, and eligibility are assessed by our credit team."),
        ("<b>Step 5: Sanction</b>", "Loan sanction letter is issued with approved loan amount, interest rate, and terms."),
        ("<b>Step 6: Legal Documentation</b>", "Loan agreement, mortgage deed, and other legal documents are executed."),
        ("<b>Step 7: Disbursement</b>", "Loan amount is disbursed directly to seller/builder as per payment schedule."),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    
    faqs = [
        ("<b>Q1: What is the maximum loan amount I can get?</b>",
         "The maximum loan amount depends on your income, age, existing obligations, and property value. Generally, we offer up to Rs. 5 crores for eligible customers."),
        
        ("<b>Q2: Can I prepay my home loan?</b>",
         "Yes, you can prepay your home loan anytime. For floating rate loans, there are no prepayment charges. For fixed rate loans, 2% + GST is charged on the prepaid amount."),
        
        ("<b>Q3: What is the difference between fixed and floating interest rates?</b>",
         "Fixed rate remains constant throughout the loan tenure, while floating rate varies based on market conditions and RBI policy changes. Floating rates are generally 0.50% lower than fixed rates."),
        
        ("<b>Q4: How is my eligibility calculated?</b>",
         "Eligibility is based on your monthly income, age, credit score, existing liabilities, and property value. As a thumb rule, your EMI should not exceed 50% of your net monthly income."),
        
        ("<b>Q5: What is the moratorium period?</b>",
         "For under-construction properties, you can opt for a moratorium period (pre-EMI) where you pay only interest during construction. Full EMI starts after possession."),
        
        ("<b>Q6: Can I get a joint home loan?</b>",
         "Yes, you can apply jointly with spouse, parents, or siblings. Joint loans increase eligibility and both applicants can claim tax benefits."),
        
        ("<b>Q7: What insurance is required?</b>",
         "Property insurance is mandatory to protect against fire, earthquake, and natural calamities. Life insurance of the borrower is recommended but not mandatory."),
        
        ("<b>Q8: How long does the approval process take?</b>",
         "In-principle approval is given within 48 hours of document submission. Complete approval with property verification takes 7-10 working days."),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Important Notes
    story.append(Paragraph("IMPORTANT NOTES", heading_style))
    notes = [
        "• Interest rates and charges mentioned are indicative and subject to change based on RBI guidelines and bank's policy.",
        "• Loan approval is subject to credit appraisal, property valuation, and verification.",
        "• The property is mortgaged to the bank until full repayment of the loan.",
        "• EMIs can be paid through auto-debit (NACH), post-dated cheques, or online transfer.",
        "• Loan accounts will be reported to credit bureaus (CIBIL, Experian, CRIF, Equifax).",
        "• For NRI customers, additional documentation and FEMA compliance is required.",
        "• Senior citizens (above 60 years) may get special interest rate concessions of up to 0.25%.",
        "• Balance transfer customers must have good repayment track record for at least 12 months.",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    # Build PDF with custom footer
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Home Loan Product Guide"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "Home Loan Product Guide"))
    
    return output_path


def create_personal_loan_doc():
    """Create comprehensive Personal Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "personal_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles  
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6)
    
    # Title
    story.append(Paragraph("PERSONAL LOAN", title_style))
    story.append(Paragraph("Instant Financial Solutions for All Your Needs", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """
    Sun National Bank Personal Loan is an unsecured loan designed to meet your immediate financial needs - 
    be it medical emergencies, wedding expenses, travel, home renovation, or any other personal requirement. 
    Get instant approval with minimal documentation and flexible repayment options.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("KEY FEATURES", heading_style))
    features = [
        ["Feature", "Details"],
        ["Loan Amount", "Rs. 50,000 to Rs. 25 lakhs"],
        ["Interest Rate", "10.49% - 18.00% p.a. (based on credit profile)"],
        ["Tenure", "12 to 60 months (1 to 5 years)"],
        ["Processing Fee", "Up to 2% of loan amount + GST"],
        ["Prepayment Charges", "Nil after 6 months\n4% + GST if prepaid within 6 months"],
        ["Documentation", "Minimal - KYC, income proof, and bank statements"],
        ["Approval Time", "Instant in-principle approval*\nDisbursement within 24 hours"],
        ["Collateral Required", "No collateral or security required"],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Paragraph("*For pre-approved customers with good credit score", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    
    eligibility = [
        ["Criteria", "Salaried", "Self-Employed"],
        ["Age", "21 - 60 years", "25 - 65 years"],
        ["Minimum Income", "Rs. 20,000 per month", "Rs. 2,50,000 per annum (ITR)"],
        ["Work Experience", "Min 1 year (6 months in current company)", "Min 2 years in business"],
        ["Credit Score (CIBIL)", "Minimum 750 for best rates\n650-749: Higher interest\nBelow 650: May be rejected", "Minimum 750 for best rates\n650-749: Higher interest\nBelow 650: May be rejected"],
        ["Nationality", "Indian Resident or NRI", "Indian Resident or NRI"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[2*inch, 2.2*inch, 2.3*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    story.append(Paragraph("For Salaried Individuals:", subheading_style))
    salaried_docs = [
        "• Identity Proof: Aadhaar Card, PAN Card, Passport, or Voter ID",
        "• Address Proof: Aadhaar, Utility bills (not older than 3 months), Passport",
        "• Income Proof: Last 3 months salary slips",
        "• Bank Statement: Last 6 months statement showing salary credits",
        "• Employment Proof: Employment certificate or offer letter",
        "• Photograph: 2 recent passport size photographs",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("For Self-Employed Individuals:", subheading_style))
    self_emp_docs = [
        "• Identity Proof: Aadhaar Card, PAN Card (mandatory)",
        "• Address Proof: Aadhaar, Utility bills, Property documents",
        "• Business Proof: GST registration, Business registration certificate, Shop license",
        "• Income Proof: IT Returns for last 2 years with computation",
        "• Bank Statement: Last 12 months business account statement",
        "• Financial Statements: Balance sheet and P&L for last 2 years (if available)",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # Interest Rate Structure
    story.append(Paragraph("INTEREST RATE STRUCTURE", heading_style))
    
    rate_info = """
    Interest rates are determined based on your credit profile, income stability, and existing relationship with the bank.
    """
    story.append(Paragraph(rate_info, normal_style))
    
    rate_data = [
        ["CIBIL Score", "Interest Rate (p.a.)", "Processing Fee"],
        ["750 and above (Excellent)", "10.49% - 12.99%", "1% of loan amount"],
        ["700 - 749 (Good)", "13.00% - 14.99%", "1.5% of loan amount"],
        ["650 - 699 (Fair)", "15.00% - 16.99%", "2% of loan amount"],
        ["600 - 649 (Poor)", "17.00% - 18.00%", "2% of loan amount"],
        ["Below 600", "Loan may not be approved", "-"],
    ]
    
    rate_table = Table(rate_data, colWidths=[2*inch, 2.5*inch, 2*inch])
    rate_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(rate_table)
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI CALCULATION EXAMPLES", heading_style))
    
    emi_data = [
        ["Loan Amount", "Interest Rate", "Tenure", "Monthly EMI", "Total Interest", "Total Payment"],
        ["Rs. 2,00,000", "11.00%", "24 months", "Rs. 9,284", "Rs. 22,816", "Rs. 2,22,816"],
        ["Rs. 5,00,000", "12.00%", "36 months", "Rs. 16,607", "Rs. 97,852", "Rs. 5,97,852"],
        ["Rs. 10,00,000", "13.00%", "48 months", "Rs. 26,783", "Rs. 12,85,584", "Rs. 22,85,584"],
        ["Rs. 15,00,000", "14.00%", "60 months", "Rs. 34,865", "Rs. 20,91,900", "Rs. 35,91,900"],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.1*inch, 1*inch, 1*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Fees and Charges
    story.append(Paragraph("FEES AND CHARGES", heading_style))
    
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "Up to 2% of loan amount + GST"],
        ["Prepayment Charges", "Nil after 6 EMI payments\n4% of principal outstanding + GST (within 6 months)"],
        ["Foreclosure Charges", "Nil after 12 EMI payments\n5% of outstanding + GST (within 12 months)"],
        ["Late Payment Charges", "2% per month on overdue amount or Rs. 500, whichever is higher"],
        ["Cheque/NACH Bounce", "Rs. 500 per instance"],
        ["Loan Cancellation", "Rs. 3,000 + GST (after approval but before disbursal)"],
        ["Statement Request", "Rs. 100 per statement"],
        ["Duplicate NOC", "Rs. 500 + GST"],
        ["EMI Swap Charges", "Rs. 500 + GST per swap"],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("LOAN APPLICATION PROCESS", heading_style))
    
    process_steps = [
        ("<b>Step 1: Apply Online/Offline</b>", "Submit application through mobile app, website, or visit branch. Provide basic KYC and income details."),
        ("<b>Step 2: Document Upload</b>", "Upload required documents digitally or submit at branch. Our team will verify within 2 hours."),
        ("<b>Step 3: Credit Assessment</b>", "Your credit score, income, and repayment capacity are evaluated. Instant decision for pre-approved customers."),
        ("<b>Step 4: Approval & Sanction</b>", "Receive sanction letter with approved amount, interest rate, tenure, and EMI details via SMS and email."),
        ("<b>Step 5: Agreement Signing</b>", "E-sign the loan agreement digitally or visit branch for physical signing. Aadhaar e-sign accepted."),
        ("<b>Step 6: Disbursement</b>", "Loan amount credited directly to your bank account within 24 hours of agreement signing."),
    ]
    
    for step_title, step_desc in process_steps:
        story.append(Paragraph(step_title, bullet_style))
        story.append(Paragraph(step_desc, normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Special Features
    story.append(Paragraph("SPECIAL FEATURES & BENEFITS", heading_style))
    
    benefits = [
        "• <b>Instant Disbursal:</b> Get money in your account within 24 hours for urgent needs",
        "• <b>Flexible Tenure:</b> Choose EMI tenure from 12 to 60 months as per your budget",
        "• <b>No Collateral:</b> Completely unsecured loan - no need to pledge any asset",
        "• <b>Minimal Documentation:</b> Only basic KYC and income proof required",
        "• <b>Free Prepayment:</b> Close your loan anytime after 6 months with zero charges",
        "• <b>Existing Customer Benefits:</b> Special rates and instant approval for existing account holders",
        "• <b>Top-up Facility:</b> Get additional loan on existing personal loan after 6 months",
        "• <b>EMI Moratorium:</b> Option to defer first EMI by 1 month (interest applicable)",
        "• <b>Insurance Options:</b> Opt for EMI protection insurance to secure your family",
        "• <b>Digital Journey:</b> Complete paperless process through mobile app",
    ]
    
    for benefit in benefits:
        story.append(Paragraph(benefit, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    
    faqs = [
        ("<b>Q1: What can I use a personal loan for?</b>",
         "Personal loan can be used for any legitimate purpose - medical emergencies, wedding, travel, education, home renovation, debt consolidation, or any other personal need. No end-use restriction."),
        
        ("<b>Q2: How is my loan amount eligibility calculated?</b>",
         "Eligibility is based on your monthly income, credit score, existing obligations, and age. Generally, your total EMI (including new loan) should not exceed 50-60% of your monthly income."),
        
        ("<b>Q3: Can I get a loan with low CIBIL score?</b>",
         "Minimum CIBIL score of 650 is required. However, better scores (750+) get lower interest rates and faster approval. Below 650, loan may be rejected or offered at higher rates."),
        
        ("<b>Q4: How quickly will I get the loan amount?</b>",
         "For pre-approved customers with good credit, instant approval and disbursal within 24 hours. For new customers, 2-3 working days after document verification."),
        
        ("<b>Q5: Can I prepay my personal loan?</b>",
         "Yes, you can prepay anytime. No charges if you prepay after 6 months. 4% + GST if prepaid within first 6 months."),
        
        ("<b>Q6: What if I miss an EMI payment?</b>",
         "Late payment charges of 2% per month or Rs. 500 (whichever higher) will be levied. It will also negatively impact your credit score. Contact us immediately if facing difficulty."),
        
        ("<b>Q7: Can I increase my loan amount after disbursal?</b>",
         "Yes, you can apply for a top-up loan after successfully paying 6 EMIs. The top-up amount depends on your repayment track record and income."),
        
        ("<b>Q8: Is income tax benefit available on personal loan?</b>",
         "No, personal loan does not offer any tax benefits under Income Tax Act. Only home loans, education loans, and business loans are eligible for tax deductions."),
        
        ("<b>Q9: Can I transfer my personal loan from another bank?</b>",
         "Yes, balance transfer is accepted if you have paid at least 6 EMIs to your current lender and have good repayment track record. Processing fee of 1% + GST applicable."),
        
        ("<b>Q10: What documents are needed for self-employed?</b>",
         "Self-employed individuals need: PAN card, Aadhaar, business proof (GST/shop license), last 2 years ITR with computation, and 12 months bank statement showing regular business transactions."),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Important Terms
    story.append(Paragraph("IMPORTANT TERMS & CONDITIONS", heading_style))
    
    terms = [
        "• Personal loan is an unsecured credit facility subject to credit appraisal and bank's discretion.",
        "• Interest rate is fixed for the entire tenure once sanctioned.",
        "• EMI date can be chosen based on your salary date (any date between 1st to 28th of month).",
        "• Loan will be reported to all credit bureaus (CIBIL, Experian, CRIF, Equifax). Ensure timely payments.",
        "• Bank reserves the right to recall the entire loan if you default on 3 consecutive EMIs.",
        "• Providing false information or documents is a criminal offense and loan will be cancelled immediately.",
        "• For NRI customers: NRO/NRE account required, FEMA compliance mandatory, rates may vary.",
        "• Insurance (EMI protection) is optional and not mandatory for loan approval.",
        "• Loan amount will be disbursed only to your bank account - cash disbursal not allowed.",
        "• Prepayment/foreclosure requests must be submitted 7 days in advance with required amount.",
        "• Processing fee is non-refundable even if loan is rejected or cancelled by customer.",
        "• All fees and charges mentioned are subject to GST as per prevailing rates.",
        "• Bank follows Fair Practice Code as per RBI guidelines for recovery and customer dealing.",
        "• Grievance redressal: Contact customer care or approach Banking Ombudsman if not resolved.",
    ]
    
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>FOR LOAN ASSISTANCE & QUERIES</b><br/>
    Customer Care: 1800-123-4567 (Toll Free) | 080-1234-5678<br/>
    Email: loans@sunnationalbank.in | personalloans@sunnationalbank.in<br/>
    Website: www.sunnationalbank.in/personal-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>Visit your nearest Sun National Bank branch or apply online 24x7</i>
    </para>
    """
    story.append(Paragraph(contact_text, styles['Normal']))
    
    # Build PDF
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Personal Loan Product Guide"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "Personal Loan Product Guide"))
    
    return output_path


def create_auto_loan_doc():
    """Create comprehensive Auto Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "auto_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles  
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6)
    
    # Title
    story.append(Paragraph("AUTO LOAN", title_style))
    story.append(Paragraph("Drive Your Dreams Home - Cars, Bikes & Commercial Vehicles", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """
    Sun National Bank Auto Loan helps you purchase your dream vehicle - new or used cars, two-wheelers, or commercial vehicles. 
    With competitive interest rates, flexible tenures up to 7 years, and hassle-free processing, we make vehicle ownership easy and affordable.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("KEY FEATURES", heading_style))
    features = [
        ["Feature", "Details"],
        ["Loan Amount", "Up to 100% on-road price (conditions apply)\nNew Car: Rs. 1 lakh - Rs. 1 crore\nUsed Car: Rs. 50,000 - Rs. 50 lakhs\nTwo-Wheeler: Rs. 30,000 - Rs. 3 lakhs"],
        ["Interest Rate", "New Car: 8.50% - 10.50% p.a.\nUsed Car: 10.50% - 13.50% p.a.\nTwo-Wheeler: 11.00% - 14.00% p.a."],
        ["Loan-to-Value (LTV)", "New Vehicles: Up to 90%\nUsed Vehicles: Up to 80%\nTwo-Wheelers: Up to 95%"],
        ["Tenure", "New Car: Up to 7 years (84 months)\nUsed Car: Up to 5 years (60 months)\nTwo-Wheeler: Up to 5 years (60 months)"],
        ["Processing Fee", "New: 1% of loan amount + GST\nUsed: 1.5% of loan amount + GST"],
        ["Prepayment Charges", "Nil after 12 months\n3% + GST if prepaid within 12 months"],
        ["Insurance", "Comprehensive insurance mandatory\nZero depreciation cover recommended"],
        ["Approval Time", "24-48 hours with instant in-principle approval"],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("TYPES OF VEHICLES COVERED", heading_style))
    
    vehicle_types = [
        "<b>1. New Cars:</b> Passenger cars from authorized dealers across all brands - Maruti, Hyundai, Tata, Mahindra, Toyota, Honda, etc.",
        "<b>2. Used Cars:</b> Cars up to 8 years old at time of loan closure. Vehicle age + loan tenure ≤ 10 years.",
        "<b>3. Two-Wheelers:</b> New and used motorcycles, scooters from all major brands - Honda, Hero, Bajaj, TVS, Royal Enfield, etc.",
        "<b>4. Commercial Vehicles:</b> Light commercial vehicles, goods carriers, taxis (separate scheme - check eligibility).",
        "<b>5. Electric Vehicles:</b> Special rates for EVs with subsidy benefits (0.25% rate discount on new EV cars).",
    ]
    
    for vtype in vehicle_types:
        story.append(Paragraph(vtype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Eligibility
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    
    eligibility = [
        ["Criteria", "Salaried", "Self-Employed"],
        ["Age", "21 - 65 years", "25 - 70 years"],
        ["Minimum Income", "Rs. 20,000 per month (metro)\nRs. 15,000 per month (non-metro)", "Rs. 3,00,000 per annum (ITR)"],
        ["Work Experience", "Min 1 year total\n(6 months current employer)", "Min 2 years in business"],
        ["Credit Score", "Minimum 700 for best rates\n650-699: Higher rate\nBelow 650: Case-to-case", "Minimum 700 for best rates\n650-699: Higher rate\nBelow 650: Case-to-case"],
        ["Down Payment", "Minimum 10% for new\n20% for used vehicles", "Minimum 15% for new\n25% for used vehicles"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    story.append(Paragraph("For Salaried Individuals:", subheading_style))
    salaried_docs = [
        "• Identity Proof: Aadhaar Card, PAN Card (mandatory)",
        "• Address Proof: Aadhaar, Passport, Utility bills",
        "• Income Proof: Last 3 months salary slips",
        "• Bank Statement: Last 6 months showing salary credits",
        "• Vehicle Documents: Proforma invoice from dealer, vehicle quotation",
        "• Photographs: 2 passport size photos",
        "• For Used Vehicles: Original RC, insurance policy, previous owner NOC, valuation report",
    ]
    for doc_item in salaried_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("For Self-Employed:", subheading_style))
    self_emp_docs = [
        "• Identity & Address: Aadhaar, PAN (mandatory)",
        "• Business Proof: GST registration, shop license, business registration",
        "• Income Proof: Last 2 years ITR with computation, audited financials",
        "• Bank Statement: Last 12 months business account statement",
        "• Vehicle Documents: Proforma invoice, quotation",
        "• For Used: RC copy, insurance, NOC, vehicle evaluation report",
    ]
    for doc_item in self_emp_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI CALCULATION EXAMPLES", heading_style))
    
    emi_data = [
        ["Vehicle Type", "Loan Amount", "Rate", "Tenure", "Monthly EMI", "Total Interest"],
        ["New Car\n(Hatchback)", "Rs. 5,00,000", "9.00%", "5 years", "Rs. 10,378", "Rs. 1,22,680"],
        ["New Car\n(Sedan)", "Rs. 10,00,000", "8.75%", "7 years", "Rs. 15,071", "Rs. 2,65,972"],
        ["Used Car\n(5 years old)", "Rs. 3,00,000", "11.50%", "4 years", "Rs. 7,822", "Rs. 75,456"],
        ["Two-Wheeler\n(New)", "Rs. 1,00,000", "12.00%", "3 years", "Rs. 3,321", "Rs. 19,556"],
        ["Electric Car\n(New - Special)", "Rs. 8,00,000", "8.25%", "5 years", "Rs. 16,258", "Rs. 1,75,480"],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 0.8*inch, 1*inch, 1*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("FEES AND CHARGES", heading_style))
    
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "New: 1% of loan amount + GST\nUsed: 1.5% of loan amount + GST\nTwo-Wheeler: 1% + GST"],
        ["Prepayment Charges", "Nil after 12 EMI payments\n3% of outstanding + GST (within 12 months)"],
        ["Foreclosure Charges", "Nil after 18 EMI payments\n4% of outstanding + GST (within 18 months)"],
        ["Late Payment Fee", "2% per month on overdue or Rs. 500 (whichever higher)"],
        ["NACH/Cheque Bounce", "Rs. 500 per bounce"],
        ["Duplicate Documents", "Rs. 250 + GST per document"],
        ["RC Transfer Assistance", "Rs. 1,000 + GST (optional service)"],
        ["Insurance Processing", "Free for policies through bank\nRs. 500 + GST for external insurance"],
        ["Vehicle Valuation", "Rs. 500 to Rs. 2,000 (based on vehicle value) - for used vehicles"],
        ["Loan Cancellation", "Rs. 2,000 + GST (post-approval, pre-disbursal)"],
    ]
    
    fees_table = Table(fees_data, colWidths=[2.5*inch, 4*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("INSURANCE REQUIREMENTS", heading_style))
    
    insurance_info = [
        "• <b>Comprehensive Insurance Mandatory:</b> Must cover own damage + third-party liability as per Motor Vehicles Act.",
        "• <b>Bank as Co-beneficiary:</b> Sun National Bank must be added as co-beneficiary/hypothecation in insurance policy.",
        "• <b>Zero Depreciation Cover:</b> Highly recommended for new vehicles (first 5 years).",
        "• <b>Return to Invoice (RTI):</b> Optional add-on for complete vehicle value protection in case of total loss.",
        "• <b>Renewal Mandatory:</b> Insurance must be renewed continuously. Non-renewal attracts penalty and loan recall.",
        "• <b>Engine Protection:</b> Recommended add-on for cars (covers engine damage due to water ingression).",
        "• <b>EMI Protection Insurance:</b> Optional cover to protect family from EMI burden in case of unfortunate events.",
    ]
    
    for info in insurance_info:
        story.append(Paragraph(info, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # FAQs
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    
    faqs = [
        ("<b>Q1: What is the maximum loan amount I can get?</b>",
         "Up to 90% of on-road price for new vehicles (10% down payment required). For used vehicles, up to 80%. Actual amount depends on your income, credit score, and repayment capacity."),
        
        ("<b>Q2: Can I buy a used car from an individual seller?</b>",
         "Yes, we provide loans for cars purchased from individuals, dealers, or online platforms. Vehicle must be registered in your city/state and not older than specified limits."),
        
        ("<b>Q3: Is hypothecation mandatory? When is it removed?</b>",
         "Yes, bank holds hypothecation on vehicle until full repayment. After loan closure, we provide NOC within 7 working days for hypothecation removal from RC."),
        
        ("<b>Q4: What happens if I want to sell the vehicle before loan closure?</b>",
         "You must close the loan first or get buyer to take loan transfer. We provide foreclosure quotation. Buyer can also take loan from us (balance transfer scheme)."),
        
        ("<b>Q5: Are there special rates for electric vehicles?</b>",
         "Yes, 0.25% discount on interest rate for new electric vehicles. This is in addition to government subsidies available under FAME II scheme."),
        
        ("<b>Q6: Can I transfer my existing auto loan from another bank?</b>",
         "Yes, balance transfer accepted if you have paid at least 12 EMIs. Rate benefits available. Processing fee 1% + GST."),
        
        ("<b>Q7: What if I miss EMI payment due to financial difficulty?</b>",
         "Contact us immediately. We may restructure your loan, extend tenure, or provide moratorium based on your situation. Ignoring EMI leads to penalties and repossession."),
        
        ("<b>Q8: Is loan insurance compulsory?</b>",
         "Vehicle insurance is mandatory by law and bank requirement. EMI protection insurance is optional but recommended for financial security of family."),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Important Terms
    story.append(Paragraph("IMPORTANT TERMS & CONDITIONS", heading_style))
    
    terms = [
        "• Vehicle must be registered in the name of loan applicant/co-applicant only.",
        "• Hypothecation in favor of Sun National Bank is mandatory until loan closure.",
        "• Comprehensive insurance with bank as co-beneficiary is compulsory throughout loan tenure.",
        "• PDC (post-dated cheques) or NACH mandate for EMI payment is mandatory.",
        "• Vehicle cannot be sold, transferred, or hypothecated to another party until loan closure.",
        "• For used vehicles: Technical and legal verification mandatory. Vehicle age + loan tenure ≤ 10 years.",
        "• Interest rate is fixed for entire tenure. Processing fee is non-refundable.",
        "• Default in 3 consecutive EMIs gives bank right to repossess vehicle as per SARFAESI Act.",
        "• RTO registration, road tax, and other charges are customer's responsibility.",
        "• Bank does not provide loans for vehicles older than the specified age limits.",
        "• Commercial vehicle loans subject to separate terms - contact branch for details.",
    ]
    
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>FOR AUTO LOAN ASSISTANCE</b><br/>
    Customer Care: 1800-123-4567 | 080-1234-5678<br/>
    Email: autoloans@sunnationalbank.in<br/>
    Website: www.sunnationalbank.in/auto-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>Visit authorized dealer or apply online - Instant in-principle approval!</i>
    </para>
    """
    story.append(Paragraph(contact_text, styles['Normal']))
    
    # Build PDF
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Auto Loan Product Guide"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "Auto Loan Product Guide"))
    
    return output_path


def create_education_loan_doc():
    """Create comprehensive Education Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "education_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=90, bottomMargin=50)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                fontSize=20, textColor=colors.HexColor('#FF8F42'),
                                spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                  fontSize=14, textColor=colors.HexColor('#0F1B2A'),
                                  spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'],
                                     fontSize=12, textColor=colors.HexColor('#FF8F42'),
                                     spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'],
                                 fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                 fontSize=10, leftIndent=20, spaceAfter=6)
    
    # Title
    story.append(Paragraph("EDUCATION LOAN", title_style))
    story.append(Paragraph("Invest in Your Future - Study in India or Abroad", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Overview
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """
    Sun National Bank Education Loan helps students pursue higher education in India or abroad. 
    We cover tuition fees, hostel expenses, books, equipment, travel, and other education-related costs. 
    With flexible repayment, moratorium period, and tax benefits under Section 80E, we make quality education accessible to all deserving students.
    """
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Features
    story.append(Paragraph("KEY FEATURES", heading_style))
    features = [
        ["Feature", "Domestic Education", "International Education"],
        ["Loan Amount", "Up to Rs. 10 lakhs (no collateral)\nRs. 10-20 lakhs (with collateral)", "Up to Rs. 1.5 crores\n(collateral mandatory above Rs. 7.5 lakhs)"],
        ["Interest Rate", "8.50% - 11.50% p.a.", "9.50% - 12.50% p.a."],
        ["Tenure", "Up to 15 years", "Up to 15 years"],
        ["Moratorium Period", "Course duration + 1 year\nor 6 months after job (whichever earlier)", "Course duration + 1 year\nor 6 months after job (whichever earlier)"],
        ["Processing Fee", "Nil for loans up to Rs. 4 lakhs\n1% + GST for above Rs. 4 lakhs", "1% of loan amount + GST"],
        ["Margin Money", "5% (up to Rs. 4 lakhs)\n15% (above Rs. 4 lakhs)", "15% for all loan amounts"],
        ["Tax Benefit", "Interest paid deductible u/s 80E for 8 years", "Interest paid deductible u/s 80E for 8 years"],
    ]
    
    features_table = Table(features, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("COURSES & INSTITUTIONS COVERED", heading_style))
    
    courses_info = [
        "<b>Graduate Courses:</b> Engineering (B.Tech/B.E.), Medical (MBBS), Management (BBA), Commerce (B.Com), Science, Arts, Diploma courses.",
        "<b>Post-Graduate:</b> M.Tech, MBA, MS, MCA, M.Com, M.Sc., Medical PG (MD/MS), CA, CFA, etc.",
        "<b>Professional Courses:</b> Chartered Accountancy, Company Secretary, CFA, Actuarial Science, etc.",
        "<b>Competitive Exam Coaching:</b> IIT-JEE, NEET, UPSC, CAT, GRE, GMAT, IELTS preparation courses (up to Rs. 2 lakhs).",
        "<b>Foreign Education:</b> Undergraduate and postgraduate courses in USA, UK, Canada, Australia, Germany, Singapore, etc.",
    ]
    
    for course in courses_info:
        story.append(Paragraph(course, bullet_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("<b>Approved Institutions:</b>", subheading_style))
    inst_info = [
        "• All IITs, NITs, IIMs, AIIMS, and other Central/State Government institutions",
        "• UGC/AICTE/MCI/PCI approved colleges and universities in India",
        "• Foreign universities listed in approved list (check with branch)",
        "• Professional institutes like ICAI, ICSI, ICWAI, Actuarial Society",
    ]
    for inst in inst_info:
        story.append(Paragraph(inst, bullet_style))
    
    story.append(PageBreak())
    
    # Expenses Covered
    story.append(Paragraph("EXPENSES COVERED UNDER LOAN", heading_style))
    
    expenses = [
        ["Expense Category", "Coverage Details"],
        ["Tuition Fees", "Full tuition and development fees charged by institution"],
        ["Hostel/Accommodation", "Hostel fees or rent for off-campus accommodation (with rent agreement)"],
        ["Books & Equipment", "Cost of textbooks, library fees, study material, laptop/equipment (with bills)"],
        ["Examination Fees", "Semester/annual exam fees, project fees, thesis submission fees"],
        ["Travel Expenses", "For foreign education: Airfare (economy class)\nFor domestic: Travel if required (limited)"],
        ["Study Tour/Project", "Educational tours, internship project costs (if part of curriculum)"],
        ["Caution Deposit", "Refundable deposits to college (to be refunded to bank)"],
        ["Building Fund", "One-time building/development fees if applicable"],
        ["Insurance Premium", "Mandatory student insurance, health insurance abroad"],
        ["Cost of Living", "For abroad: Living expenses as per norm (varies by country)"],
    ]
    
    expenses_table = Table(expenses, colWidths=[2*inch, 4.5*inch])
    expenses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    
    eligibility = [
        ["Criteria", "Student", "Co-Applicant (Parent/Guardian)"],
        ["Age", "18 years and above\n(at time of loan)", "21 - 65 years"],
        ["Academic Record", "Admission confirmed in approved institution\nGood academic record (60%+ in qualifying exam)", "Not applicable"],
        ["Co-borrower", "Mandatory requirement\n(Parent/Guardian/Spouse)", "Income proof mandatory\nGood credit score required"],
        ["Income Requirement", "Not applicable for student", "Minimum Rs. 2 lakhs p.a. for domestic\nRs. 3 lakhs p.a. for international"],
        ["Credit Score", "Not applicable\n(Student may not have credit history)", "Minimum 650 (700+ preferred)"],
        ["Nationality", "Indian citizen", "Indian citizen or NRI parent"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    
    story.append(Paragraph("Student Documents:", subheading_style))
    student_docs = [
        "• Identity Proof: Aadhaar Card, PAN Card, Passport (for foreign education)",
        "• Admission Proof: Admission letter/offer letter from institution (must be unconditional)",
        "• Academic Records: 10th, 12th, Graduation mark sheets and certificates",
        "• Entrance Exam Scorecard: JEE, NEET, CAT, GRE, GMAT, IELTS, etc. (if applicable)",
        "• Fee Structure: Official fee schedule from institution for entire course duration",
        "• Scholarship Letter: If any scholarship sanctioned, provide approval letter",
        "• Passport: For international education (mandatory)",
        "• Visa Documents: I-20 (USA), CAS (UK), COE (Australia), etc. as applicable",
    ]
    for doc_item in student_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Co-Applicant (Parent/Guardian) Documents:", subheading_style))
    parent_docs = [
        "• Identity & Address: Aadhaar, PAN Card (both mandatory)",
        "• Income Proof: Last 6 months salary slips (salaried) or last 2 years ITR (self-employed)",
        "• Bank Statements: Last 6 months for salaried, 12 months for self-employed",
        "• Employment Proof: Employment certificate, appointment letter",
        "• Property Documents: If offering collateral (property papers, valuation report)",
        "• Relationship Proof: Birth certificate, Aadhaar, or any document showing relationship with student",
    ]
    for doc_item in parent_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(PageBreak())
    
    # Repayment Structure
    story.append(Paragraph("REPAYMENT STRUCTURE & MORATORIUM", heading_style))
    
    repayment_info = """
    Education loan repayment is designed to be student-friendly with moratorium period and flexible options:
    """
    story.append(Paragraph(repayment_info, normal_style))
    
    repay_phases = [
        ("<b>Phase 1 - Study Period (Course Duration):</b>",
         "During this phase, EMI payment is not required. However, you may choose to pay interest-only EMI to reduce overall interest burden (optional)."),
        
        ("<b>Phase 2 - Moratorium Period:</b>",
         "After course completion, you get moratorium of course duration + 1 year or 6 months after getting job (whichever is earlier). " 
         "During this period, no EMI payment required, but interest gets added to principal (compounding)."),
        
        ("<b>Phase 3 - Repayment Period:</b>",
         "Regular EMI starts after moratorium ends. Tenure can be up to 15 years. You can choose monthly, quarterly, or bullet repayment options."),
    ]
    
    for phase_title, phase_desc in repay_phases:
        story.append(Paragraph(phase_title, subheading_style))
        story.append(Paragraph(phase_desc, normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Special Options:</b>", subheading_style))
    special_options = [
        "• <b>Simple Interest during Study:</b> Option to pay interest-only EMI during study to save on total interest",
        "• <b>Partial Payment:</b> Make lump sum prepayments anytime without charges to reduce principal",
        "• <b>Step-up EMI:</b> Start with lower EMI and increase annually as income grows",
        "• <b>Flexible Tenure:</b> Choose repayment tenure from 5 to 15 years based on comfort",
    ]
    for option in special_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # EMI Examples
    story.append(Paragraph("EMI CALCULATION EXAMPLES", heading_style))
    story.append(Paragraph("(Assuming moratorium interest is capitalized and EMI starts after course completion + 1 year)", normal_style))
    
    emi_data = [
        ["Course", "Total Loan", "Rate", "Course+Moratorium", "Repay Tenure", "Monthly EMI"],
        ["B.Tech (India)", "Rs. 8,00,000", "9.00%", "4+1 = 5 years", "10 years", "Rs. 13,927"],
        ["MBA (India)", "Rs. 15,00,000", "9.50%", "2+1 = 3 years", "10 years", "Rs. 26,199"],
        ["MS (USA)", "Rs. 50,00,000", "10.50%", "2+1 = 3 years", "15 years", "Rs. 71,955"],
        ["MBBS (India)", "Rs. 25,00,000", "8.75%", "5.5+1 = 6.5 years", "15 years", "Rs. 43,462"],
    ]
    
    emi_table = Table(emi_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 1.1*inch, 1*inch, 1*inch])
    emi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(emi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Tax Benefits
    story.append(Paragraph("INCOME TAX BENEFITS (Section 80E)", heading_style))
    
    tax_info = [
        "• <b>Deduction on Interest:</b> Interest paid on education loan is fully deductible from taxable income under Section 80E.",
        "• <b>Duration:</b> Benefit available for maximum 8 years starting from year of first EMI payment.",
        "• <b>No Upper Limit:</b> There is NO MAXIMUM LIMIT on deduction amount - entire interest paid is deductible.",
        "• <b>Who Can Claim:</b> Loan must be taken by individual (parent/student). HUF or companies cannot claim.",
        "• <b>Course Requirement:</b> Loan must be for higher education (after 12th standard) for self, spouse, or children.",
        "• <b>Lender Requirement:</b> Loan must be from bank, financial institution, or approved charity. Not from relatives.",
        "• <b>Certificate Required:</b> Bank will provide interest certificate annually for IT return filing.",
    ]
    
    for tax_point in tax_info:
        story.append(Paragraph(tax_point, bullet_style))
    
    story.append(Spacer(1, 0.15*inch))
    tax_example = """
    <b>Example:</b> If you paid Rs. 1,50,000 as interest in a year and you are in 30% tax bracket, 
    you save Rs. 45,000 in tax (Rs. 1,50,000 × 30% = Rs. 45,000). This benefit is available for 8 consecutive assessment years.
    """
    story.append(Paragraph(tax_example, normal_style))
    
    story.append(PageBreak())
    
    # Fees and Charges
    story.append(Paragraph("FEES AND CHARGES", heading_style))
    
    fees_data = [
        ["Charge Type", "Domestic", "International"],
        ["Processing Fee", "Nil (up to Rs. 4 lakhs)\n1% + GST (above Rs. 4 lakhs)", "1% of loan amount + GST"],
        ["Prepayment/Foreclosure", "Nil - No charges for prepayment anytime", "Nil - No charges for prepayment anytime"],
        ["Late Payment Fee", "Rs. 500 or 2% per month (whichever higher) on overdue amount", "Rs. 500 or 2% per month (whichever higher) on overdue amount"],
        ["Cheque/NACH Bounce", "Rs. 500 per bounce", "Rs. 500 per bounce"],
        ["Loan Restructuring Fee", "Rs. 1,000 + GST (if tenure modified)", "Rs. 1,000 + GST (if tenure modified)"],
        ["Duplicate Certificate", "Rs. 250 + GST", "Rs. 250 + GST"],
        ["Collateral Valuation", "As per actual (Rs. 500 to Rs. 3,000)", "As per actual (Rs. 2,000 to Rs. 5,000)"],
    ]
    
    fees_table = Table(fees_data, colWidths=[2.2*inch, 2.2*inch, 2.1*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
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
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    
    faqs = [
        ("<b>Q1: Can I get loan without collateral?</b>",
         "Yes, for loans up to Rs. 7.5 lakhs, no collateral required. Third-party guarantee may be needed. Above Rs. 7.5 lakhs, collateral (property/FD/LIC) is mandatory."),
        
        ("<b>Q2: What if I don't get admission? Will fees be refunded?</b>",
         "Yes, processing fee is refunded if admission is not confirmed. Loan is sanctioned only after unconditional admission offer is received."),
        
        ("<b>Q3: Can I change institution after loan is approved?</b>",
         "Yes, but you must inform bank immediately. New institution must be approved and loan may be re-evaluated based on new course fee."),
        
        ("<b>Q4: Who will receive the loan amount - student or institution?</b>",
         "Loan is disbursed directly to institution for tuition fees. For other expenses like hostel, books, it may be given to student account."),
        
        ("<b>Q5: When do I start paying EMI?</b>",
         "EMI starts after moratorium period (course + 1 year or 6 months after job). However, you can voluntarily start paying interest during study to save total cost."),
        
        ("<b>Q6: What if I get scholarship later?</b>",
         "Inform bank immediately. Scholarship amount will be adjusted and loan amount may be reduced. This helps lower your EMI burden."),
        
        ("<b>Q7: Can parent claim tax benefit if student is loan borrower?</b>",
         "Tax benefit under 80E is available only to the person who has taken loan in their name. If loan is in student's name, only student can claim (once they start earning)."),
        
        ("<b>Q8: What if I can't get job after course completion?</b>",
         "Inform bank immediately. We may extend moratorium by 6 months to 1 year or restructure loan. Communication is key - don't default silently."),
        
        ("<b>Q9: Is loan available for distance learning or online courses?</b>",
         "Loan is primarily for full-time regular courses. Some online/distance courses from reputed institutions may be considered on case-to-case basis."),
        
        ("<b>Q10: What documents needed for foreign university?</b>",
         "Unconditional admission offer, I-20/CAS/COE, IELTS/TOEFL/GRE scores, passport, visa application, fee structure for entire course, and parent's financial documents."),
    ]
    
    for question, answer in faqs:
        story.append(Paragraph(question, bullet_style))
        story.append(Paragraph(answer, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Important Notes
    story.append(Paragraph("IMPORTANT POINTS TO REMEMBER", heading_style))
    
    notes = [
        "• Co-borrower (parent/guardian) is mandatory for all education loans.",
        "• Admission must be to UGC/AICTE/MCI approved institutions or recognized foreign universities.",
        "• Interest starts accruing from date of first disbursal, not from EMI start date.",
        "• During moratorium, interest is compounded and added to principal if not paid.",
        "• Paying interest during study period significantly reduces total loan cost.",
        "• For foreign education, loan covers tuition + living expenses as per country norms.",
        "• Margin money (5-15%) must be paid by student/parent - not covered in loan.",
        "• Loan can be disbursed in multiple installments based on semester/year fee payment schedule.",
        "• Prepayment is encouraged - no charges. Helps reduce interest burden substantially.",
        "• Maintain good credit score by timely EMI - impacts future loans (home, car, etc.).",
    ]
    
    for note in notes:
        story.append(Paragraph(note, bullet_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    contact_text = """
    <para align=center>
    <b>FOR EDUCATION LOAN ASSISTANCE</b><br/>
    Customer Care: 1800-123-4567 | 080-1234-5678<br/>
    Email: educationloans@sunnationalbank.in<br/>
    Website: www.sunnationalbank.in/education-loan<br/>
    WhatsApp: +91-98765-43210<br/><br/>
    <i>Invest in knowledge - it pays the best interest!</i>
    </para>
    """
    story.append(Paragraph(contact_text, styles['Normal']))
    
    # Build PDF
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Education Loan Product Guide"),
              onLaterPages=lambda c, d: create_header_footer(c, d, "Education Loan Product Guide"))
    
    return output_path


def create_business_loan_doc():
    """Create comprehensive Business Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "business_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#FF8F42'), spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6)
    
    story.append(Paragraph("BUSINESS LOAN", title_style))
    story.append(Paragraph("Fuel Your Business Growth - MSME & SME Financing", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """Sun National Bank Business Loan is designed for Micro, Small & Medium Enterprises (MSMEs) to meet working capital needs, expansion, equipment purchase, or any business requirement. We support entrepreneurs with flexible financing options including MUDRA loans, term loans, and working capital facilities."""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    features = [
        ["Feature", "MUDRA Loan", "SME Term Loan", "Working Capital"],
        ["Loan Amount", "Rs. 10,000 - Rs. 10 lakhs\n(Shishu/Kishore/Tarun)", "Rs. 10 lakhs - Rs. 50 crores", "Rs. 5 lakhs - Rs. 25 crores"],
        ["Interest Rate", "7.50% - 10.00% p.a.", "10.00% - 14.00% p.a.", "11.00% - 15.00% p.a."],
        ["Tenure", "Up to 7 years", "Up to 10 years", "12 months (renewable)"],
        ["Collateral", "Not required\n(up to Rs. 10 lakhs)", "Required above Rs. 25 lakhs", "Required above Rs. 50 lakhs"],
        ["Processing Fee", "0.50% - 1% + GST", "1.5% - 2% + GST", "1% + GST"],
    ]
    
    features_table = Table(features, colWidths=[1.5*inch, 1.6*inch, 1.6*inch, 1.8*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("TYPES OF BUSINESS LOANS", heading_style))
    loan_types = [
        "<b>1. MUDRA Loans:</b> Government scheme for micro enterprises. Shishu (up to Rs. 50,000), Kishore (Rs. 50,001 to Rs. 5 lakhs), Tarun (Rs. 5,00,001 to Rs. 10 lakhs).",
        "<b>2. Term Loans:</b> For capital expenditure - machinery, equipment, factory setup, expansion. Fixed tenure with monthly/quarterly EMI.",
        "<b>3. Working Capital Loan:</b> For day-to-day operations - raw material, salaries, rent. Overdraft or cash credit limit facility.",
        "<b>4. Invoice Financing:</b> Get instant funds against pending invoices/bills. Up to 80% of invoice value. Interest only on utilized amount.",
        "<b>5. Equipment Financing:</b> Finance machinery, vehicles, computers, tools. Equipment acts as collateral. Up to 90% funding.",
        "<b>6. Business Overdraft:</b> Withdraw funds as needed up to sanctioned limit. Interest only on utilized amount, not entire limit.",
    ]
    for ltype in loan_types:
        story.append(Paragraph(ltype, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    eligibility = [
        ["Criteria", "Requirement"],
        ["Business Type", "Proprietorship, Partnership, Private Limited, LLP, Co-operatives"],
        ["Business Vintage", "Minimum 2 years (3 years for loans above Rs. 50 lakhs)"],
        ["Turnover", "MUDRA: No minimum\nSME: Minimum Rs. 10 lakhs p.a.\nLarge: As per requirement"],
        ["Age", "Proprietor/Partner: 21-65 years"],
        ["GST Registration", "Mandatory for turnover > Rs. 40 lakhs or as per GST Act"],
        ["ITR Filing", "Last 2 years ITR mandatory (3 years for large loans)"],
        ["CIBIL Score", "Minimum 650 (business & personal)\n700+ for best rates"],
        ["Profitability", "Business should be profitable for at least last 1 year"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[2*inch, 4.5*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    docs_list = [
        "• <b>KYC:</b> Aadhaar, PAN of all partners/directors (mandatory)",
        "• <b>Business Proof:</b> GST registration, Shop/Establishment license, MSME/Udyog Aadhaar certificate",
        "• <b>Financial Documents:</b> Last 2-3 years ITR with computation, audited financials (P&L, Balance Sheet)",
        "• <b>Bank Statements:</b> Last 12 months current account statement showing business transactions",
        "• <b>Business Profile:</b> Company profile, list of clients, purchase orders, ongoing contracts",
        "• <b>Ownership Proof:</b> Office/factory ownership documents or rent agreement with NOC",
        "• <b>Projected Financials:</b> For new expansion - detailed project report, estimated cost",
        "• <b>Collateral Documents:</b> Property papers, valuation report (if offering collateral)",
        "• <b>Existing Loans:</b> Sanction letters and statements of existing business loans",
    ]
    for doc_item in docs_list:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("FEES & CHARGES", heading_style))
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "0.50% - 2% of loan amount + GST (based on loan type)"],
        ["Prepayment Charges", "2% - 4% + GST (if prepaid before 12 months)\nNil after 12 months"],
        ["Late Payment", "2% - 3% per month on overdue amount"],
        ["Penal Interest", "Additional 2% p.a. on default amount"],
        ["Document Charges", "Rs. 500 - Rs. 2,000 + GST"],
        ["Legal/Technical Charges", "As per actuals (Rs. 2,000 - Rs. 10,000)"],
        ["Inspection Charges", "Rs. 1,000 per inspection for project loans"],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    faqs = [
        ("<b>Q1: What is MUDRA loan?</b>", "MUDRA (Micro Units Development & Refinance Agency) is government scheme for micro enterprises up to Rs. 10 lakhs without collateral."),
        ("<b>Q2: Can startups apply for business loan?</b>", "Yes, but minimum 2 years business vintage required. For fresh startups, explore government schemes like Startup India or PMEGP."),
        ("<b>Q3: Is GST registration mandatory?</b>", "Yes, if your turnover exceeds Rs. 40 lakhs or as per GST Act. For smaller businesses under MUDRA, may not be mandatory."),
        ("<b>Q4: What is working capital loan?</b>", "It's a credit facility for day-to-day operations. You get a limit and can withdraw as needed. Interest charged only on utilized amount."),
        ("<b>Q5: Can I get loan for business losses?</b>", "No, loan is for growth and expansion. Business should show profitability. Loss-making businesses are high risk and generally not financed."),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    contact_text = """<para align=center><b>FOR BUSINESS LOAN ASSISTANCE</b><br/>Customer Care: 1800-123-4567<br/>Email: businessloans@sunnationalbank.in<br/>Website: www.sunnationalbank.in/business-loan</para>"""
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Business Loan Product Guide"), onLaterPages=lambda c, d: create_header_footer(c, d, "Business Loan Product Guide"))
    return output_path


def create_gold_loan_doc():
    """Create comprehensive Gold Loan product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "gold_loan_product_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6)
    
    story.append(Paragraph("GOLD LOAN", title_style))
    story.append(Paragraph("Quick Cash Against Your Gold Ornaments - Instant Approval", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """Get instant cash by pledging your gold ornaments/coins/bars. Sun National Bank Gold Loan offers up to 75% of gold value (as per RBI guidelines) with flexible repayment options. Your gold is stored safely in bank lockers with full insurance coverage."""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    features = [
        ["Feature", "Details"],
        ["Loan Amount", "Rs. 10,000 to Rs. 1 crore (based on gold value)"],
        ["Loan-to-Value (LTV)", "Up to 75% of gold value (as per RBI norms)"],
        ["Interest Rate", "7.00% - 12.00% p.a. (based on amount and tenure)"],
        ["Tenure", "3 months to 36 months"],
        ["Processing Fee", "0.50% - 1% + GST (minimum Rs. 500)"],
        ["Gold Purity Accepted", "18 Karat to 24 Karat gold"],
        ["Disbursal Time", "Within 30 minutes of gold verification"],
        ["Prepayment", "Allowed anytime without charges"],
    ]
    
    features_table = Table(features, colWidths=[2*inch, 4.5*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("TYPES OF GOLD ACCEPTED", heading_style))
    gold_types = [
        "• <b>Gold Ornaments:</b> Necklaces, bangles, chains, rings, earrings (must be 18K - 24K purity)",
        "• <b>Gold Coins:</b> Coins purchased from banks or certified dealers (purity certificate required)",
        "• <b>Gold Bars/Biscuits:</b> Gold bars with purity hallmark from recognized agencies",
        "• <b>Note:</b> Studded jewelry accepted based on gold weight only (stone value not considered)",
    ]
    for gtype in gold_types:
        story.append(Paragraph(gtype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("REPAYMENT OPTIONS", heading_style))
    repay_options = [
        "<b>1. Regular EMI:</b> Pay fixed EMI every month (principal + interest)",
        "<b>2. Bullet Repayment:</b> Pay only interest monthly, repay full principal at end",
        "<b>3. Interest Servicing:</b> Pay interest periodically, close principal anytime",
        "<b>4. One-time Payment:</b> Pay interest and principal together at loan maturity",
    ]
    for option in repay_options:
        story.append(Paragraph(option, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("ELIGIBILITY & DOCUMENTS", heading_style))
    eligibility = [
        "• <b>Age:</b> 18 to 70 years",
        "• <b>KYC Documents:</b> Aadhaar Card, PAN Card",
        "• <b>Ownership Proof:</b> Purchase bill/invoice of gold (if available - not mandatory)",
        "• <b>Income Proof:</b> Not required - loan is against gold collateral",
        "• <b>Credit Score:</b> Not required - gold acts as security",
    ]
    for elig in eligibility:
        story.append(Paragraph(elig, bullet_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("GOLD VALUATION PROCESS", heading_style))
    valuation = [
        "<b>Step 1:</b> Gold ornaments tested for purity using non-destructive XRF machine (no damage to ornaments)",
        "<b>Step 2:</b> Weight measured on certified electronic weighing scale",
        "<b>Step 3:</b> Loan value calculated: Weight × Purity % × Current gold rate × LTV (75%)",
        "<b>Step 4:</b> Gold rate as per bank's rate card (based on market price)",
        "<b>Example:</b> 100 grams of 22K gold @ Rs. 6,000/gram = Rs. 6,00,000 value. Loan: 75% = Rs. 4,50,000",
    ]
    for val in valuation:
        story.append(Paragraph(val, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("FEES & CHARGES", heading_style))
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "0.50% - 1% + GST (Min Rs. 500, Max Rs. 10,000)"],
        ["Prepayment/Foreclosure", "Nil - Close anytime without charges"],
        ["Late Payment Fee", "2% per month on overdue amount"],
        ["Valuation Charges", "Free - No gold testing charges"],
        ["Storage & Insurance", "Free - Bank bears all storage and insurance cost"],
        ["Duplicate Documents", "Rs. 100 per document"],
        ["Loan Renewal Charges", "Rs. 500 + GST (if tenure extended)"],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("LOAN CLOSURE & GOLD RETURN", heading_style))
    closure_process = [
        "• Pay full outstanding amount (principal + interest + charges)",
        "• Gold returned within 30 minutes of payment clearance",
        "• Verify ornaments - same items with identification marks will be returned",
        "• Get loan closure certificate and NOC from bank",
        "• Partial release: Pay proportionate amount and release some gold items",
    ]
    for step in closure_process:
        story.append(Paragraph(step, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("IMPORTANT TERMS & CONDITIONS", heading_style))
    terms = [
        "• RBI guideline: Maximum LTV is 75% of gold value for all gold loans",
        "• Gold stored in bank's secure locker with full insurance coverage",
        "• If EMI not paid for 12 months, bank has right to auction gold (after due notice)",
        "• Auction surplus (if any) will be returned to customer after adjusting dues",
        "• Interest rate is fixed for loan tenure - not linked to gold rate fluctuations",
        "• Gold ornaments will be melted ONLY in case of auction, not otherwise",
        "• Customer can top-up loan anytime by pledging additional gold",
        "• Early closure encouraged - no prepayment charges at all",
        "• Photo/video documentation of gold done for transparency",
    ]
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    faqs = [
        ("<b>Q1: Will my gold ornaments be damaged during testing?</b>", "No, we use XRF technology which is non-destructive. Your ornaments remain intact."),
        ("<b>Q2: What if gold rate increases after taking loan?</b>", "Your EMI and interest remain same. Gold rate fluctuation doesn't affect existing loan terms."),
        ("<b>Q3: Can I take additional loan on same gold?</b>", "No, but you can close existing loan and take fresh loan at current rates. Or pledge additional gold for top-up."),
        ("<b>Q4: Is hallmarked gold mandatory?</b>", "Not mandatory. We test purity using XRF machine. But hallmark helps in faster processing."),
        ("<b>Q5: What happens if I don't repay?</b>", "After 12 months default, bank can auction gold as per RBI guidelines. Notice will be sent before auction."),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    contact_text = """<para align=center><b>FOR GOLD LOAN ASSISTANCE</b><br/>Customer Care: 1800-123-4567<br/>Email: goldloan@sunnationalbank.in<br/>Website: www.sunnationalbank.in/gold-loan<br/><i>Get instant cash in 30 minutes!</i></para>"""
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Gold Loan Product Guide"), onLaterPages=lambda c, d: create_header_footer(c, d, "Gold Loan Product Guide"))
    return output_path


def create_loan_against_property_doc():
    """Create comprehensive Loan Against Property product documentation"""
    output_path = Path(__file__).parent / "loan_products" / "loan_against_property_guide.pdf"
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=72, leftMargin=72, topMargin=90, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#FF8F42'), spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F1B2A'), spaceAfter=12, spaceBefore=16, fontName='Helvetica-Bold')
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#FF8F42'), spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, spaceAfter=10)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6)
    
    story.append(Paragraph("LOAN AGAINST PROPERTY (LAP)", title_style))
    story.append(Paragraph("Unlock Your Property Value for Any Purpose - Business or Personal", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("PRODUCT OVERVIEW", heading_style))
    overview_text = """Loan Against Property (LAP) allows you to leverage your residential or commercial property to meet any financial requirement - business expansion, working capital, education, medical emergency, or debt consolidation. Property remains in your possession while you get substantial funds at attractive interest rates."""
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    features = [
        ["Feature", "Residential Property", "Commercial Property"],
        ["Loan Amount", "Rs. 5 lakhs to Rs. 10 crores", "Rs. 10 lakhs to Rs. 25 crores"],
        ["LTV (Loan to Value)", "Up to 60% of market value", "Up to 55% of market value"],
        ["Interest Rate", "9.00% - 12.00% p.a.", "10.00% - 14.00% p.a."],
        ["Tenure", "Up to 20 years", "Up to 15 years"],
        ["Processing Fee", "1% - 2% of loan amount + GST", "1.5% - 2.5% + GST"],
        ["Prepayment Charges", "Nil after 12 months\n4% + GST within 12 months", "Nil after 18 months\n5% + GST within 18 months"],
        ["Usage", "Any personal or business purpose", "Business purpose primarily"],
    ]
    
    features_table = Table(features, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(features_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("TYPES OF PROPERTIES ACCEPTED", heading_style))
    property_types = [
        "<b>Residential:</b> Self-occupied or rented - apartments, independent houses, villas, bungalows (must have clear title)",
        "<b>Commercial:</b> Offices, shops, showrooms, warehouses, industrial sheds (rented or self-used)",
        "<b>Plot/Land:</b> Residential or commercial plots with approved plans (in some cases)",
        "<b>Note:</b> Property must be in borrower's name or co-applicant's name. Agricultural land NOT accepted.",
    ]
    for ptype in property_types:
        story.append(Paragraph(ptype, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("ELIGIBILITY CRITERIA", heading_style))
    eligibility = [
        ["Criteria", "Salaried", "Self-Employed/Business"],
        ["Age", "21 - 65 years", "25 - 70 years"],
        ["Income", "Minimum Rs. 50,000 per month", "Minimum Rs. 6 lakhs per annum (ITR)"],
        ["Work Experience", "Min 2 years total", "Min 3 years in business"],
        ["Credit Score", "Minimum 700 (750+ for best rates)", "Minimum 700 (750+ for best rates)"],
        ["Property Age", "Up to 30 years at loan maturity", "Up to 25 years at loan maturity"],
        ["Ownership", "Self-owned or co-applicant owned", "Self/company/partnership owned"],
    ]
    
    eligibility_table = Table(eligibility, colWidths=[1.8*inch, 2.3*inch, 2.4*inch])
    eligibility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1B2A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eligibility_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("DOCUMENTS REQUIRED", heading_style))
    story.append(Paragraph("Personal Documents:", subheading_style))
    personal_docs = [
        "• KYC: Aadhaar Card, PAN Card (mandatory)",
        "• Income Proof: Last 6 months salary slips / Last 2 years ITR with computation",
        "• Bank Statements: Last 12 months for all operative accounts",
        "• Employment Proof: Employment letter, business registration certificate",
    ]
    for doc_item in personal_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Paragraph("Property Documents:", subheading_style))
    property_docs = [
        "• Sale Deed/Title Deed - Registered copy showing clear ownership",
        "• Chain of Title - Previous sale deeds (last 13-30 years as per state)",
        "• Encumbrance Certificate (EC) - Last 13-30 years showing no pending dues",
        "• Property Tax Receipts - Latest paid receipts",
        "• Building Approval Plan - Municipal corporation approved plan",
        "• Occupancy Certificate / Completion Certificate",
        "• NOC from Builder/Society (if applicable)",
        "• Property Valuation Report - Bank empaneled valuer will inspect",
        "• If Mortgaged: NOC from existing lender or loan closure certificate",
    ]
    for doc_item in property_docs:
        story.append(Paragraph(doc_item, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("LOAN PROCESSING STAGES", heading_style))
    stages = [
        "<b>Stage 1 - Application:</b> Submit application with KYC and income documents",
        "<b>Stage 2 - Property Valuation:</b> Bank empaneled engineer inspects property (3-5 days)",
        "<b>Stage 3 - Legal Verification:</b> Bank lawyer verifies all property documents (7-10 days)",
        "<b>Stage 4 - Technical Verification:</b> Technical team verifies building quality, age, compliance",
        "<b>Stage 5 - Credit Assessment:</b> Income, CIBIL, repayment capacity evaluated",
        "<b>Stage 6 - Sanction:</b> Loan sanctioned with amount, rate, tenure details",
        "<b>Stage 7 - Documentation:</b> Loan agreement, mortgage deed executed and registered",
        "<b>Stage 8 - Disbursal:</b> Amount credited to bank account post all documentation",
    ]
    for stage in stages:
        story.append(Paragraph(stage, bullet_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("FEES & CHARGES", heading_style))
    fees_data = [
        ["Charge Type", "Amount"],
        ["Processing Fee", "1% - 2.5% of loan amount + GST"],
        ["Property Valuation", "Rs. 3,000 - Rs. 10,000 (based on property value)"],
        ["Legal Charges", "Rs. 5,000 - Rs. 15,000 + stamp duty on mortgage deed"],
        ["Prepayment Charges", "Nil after 12-18 months\n4-5% + GST if within 12-18 months"],
        ["Late Payment Fee", "2% per month on overdue or Rs. 500 (whichever higher)"],
        ["NACH Bounce", "Rs. 500 per bounce"],
        ["Part-payment Charges", "Nil - Make lump sum payments anytime"],
        ["Duplicate Documents", "Rs. 500 per document set"],
    ]
    
    fees_table = Table(fees_data, colWidths=[3*inch, 3.5*inch])
    fees_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF8F42')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FBFF')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(fees_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("FREQUENTLY ASKED QUESTIONS", heading_style))
    faqs = [
        ("<b>Q1: Can I use the money for any purpose?</b>", "Yes, LAP is multipurpose loan. Use for business, education, medical, marriage, or any other legitimate purpose. No restrictions."),
        ("<b>Q2: Will I have to vacate the property?</b>", "No, property remains in your possession. Bank only holds mortgage rights until loan is repaid. You can stay/use/rent it."),
        ("<b>Q3: How is property value determined?</b>", "Bank empaneled valuer inspects property and provides valuation report based on location, size, age, market rates, and condition."),
        ("<b>Q4: Can I mortgage property in someone else's name?</b>", "Property must be in your name or co-applicant's name. Co-owner must be co-applicant in loan."),
        ("<b>Q5: What if I already have home loan on property?</b>", "Property with existing loan NOT accepted. You must close existing loan first or do balance transfer + top-up to our bank."),
        ("<b>Q6: Is property insurance mandatory?</b>", "Yes, property must be insured against fire, earthquake, and other natural calamities with bank as co-beneficiary."),
    ]
    
    for q, a in faqs:
        story.append(Paragraph(q, bullet_style))
        story.append(Paragraph(a, normal_style))
        story.append(Spacer(1, 0.08*inch))
    
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("IMPORTANT TERMS", heading_style))
    terms = [
        "• Property must have clear and marketable title - free from all encumbrances",
        "• Loan tenure + property age should not exceed 50 years",
        "• Property insurance with bank as co-beneficiary is mandatory",
        "• Mortgage deed must be registered at sub-registrar office (customer bears stamp duty)",
        "• Default for 3 consecutive months gives bank right to invoke SARFAESI Act",
        "• Under SARFAESI, bank can take possession and sell property without court order (after 60 days notice)",
        "• Property cannot be sold or transferred until loan is fully repaid and mortgage is released",
        "• Interest rate is fixed for entire tenure - no floating rate option",
    ]
    for term in terms:
        story.append(Paragraph(term, bullet_style))
    
    contact_text = """<para align=center><b>FOR LOAN AGAINST PROPERTY</b><br/>Customer Care: 1800-123-4567<br/>Email: lap@sunnationalbank.in<br/>Website: www.sunnationalbank.in/loan-against-property</para>"""
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story, onFirstPage=lambda c, d: create_header_footer(c, d, "Loan Against Property Guide"), onLaterPages=lambda c, d: create_header_footer(c, d, "Loan Against Property Guide"))
    return output_path


if __name__ == "__main__":
    print("Creating comprehensive loan product documentation for Sun National Bank (India)...")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "loan_products"
    output_dir.mkdir(exist_ok=True)
    
    # Create all loan product guides
    docs_created = []
    
    print("\n1️⃣  Generating Home Loan Product Guide...")
    home_loan_path = create_home_loan_doc()
    docs_created.append(("Home Loan", home_loan_path))
    print(f"   ✓ Created: {home_loan_path.name}")
    
    print("\n2️⃣  Generating Personal Loan Product Guide...")
    personal_loan_path = create_personal_loan_doc()
    docs_created.append(("Personal Loan", personal_loan_path))
    print(f"   ✓ Created: {personal_loan_path.name}")
    
    print("\n3️⃣  Generating Auto Loan Product Guide...")
    auto_loan_path = create_auto_loan_doc()
    docs_created.append(("Auto Loan", auto_loan_path))
    print(f"   ✓ Created: {auto_loan_path.name}")
    
    print("\n4️⃣  Generating Education Loan Product Guide...")
    education_loan_path = create_education_loan_doc()
    docs_created.append(("Education Loan", education_loan_path))
    print(f"   ✓ Created: {education_loan_path.name}")
    
    print("\n5️⃣  Generating Business Loan Product Guide...")
    business_loan_path = create_business_loan_doc()
    docs_created.append(("Business Loan", business_loan_path))
    print(f"   ✓ Created: {business_loan_path.name}")
    
    print("\n6️⃣  Generating Gold Loan Product Guide...")
    gold_loan_path = create_gold_loan_doc()
    docs_created.append(("Gold Loan", gold_loan_path))
    print(f"   ✓ Created: {gold_loan_path.name}")
    
    print("\n7️⃣  Generating Loan Against Property Guide...")
    lap_path = create_loan_against_property_doc()
    docs_created.append(("Loan Against Property", lap_path))
    print(f"   ✓ Created: {lap_path.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully created {len(docs_created)} comprehensive loan product guides!")
    print(f"📁 Location: {output_dir}")
    print("\n📚 Documents created for RAG:")
    for idx, (loan_type, path) in enumerate(docs_created, 1):
        print(f"   {idx}. {loan_type}: {path.name}")
    print("\n💡 These documents contain detailed information about:")
    print("   • Interest rates and charges")
    print("   • Eligibility criteria")
    print("   • Required documents")
    print("   • Loan process and timeline")
    print("   • FAQs and important terms")
    print("   • India-specific regulations and compliance")
