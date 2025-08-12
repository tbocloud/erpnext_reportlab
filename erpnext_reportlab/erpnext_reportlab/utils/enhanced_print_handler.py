# Copyright (c) 2025, sammish and contributors
# Enhanced PDF Print Format Handler

import frappe
from frappe.utils.print_format import download_pdf

@frappe.whitelist()
def enhanced_download_pdf(doctype, name, format=None, doc=None, no_letterhead=0, language=None, letterhead=None):
    """Enhanced PDF download with ReportLab rendering"""
    
    try:
        # Get the document
        if not doc:
            doc = frappe.get_doc(doctype, name)
        
        # Create enhanced PDF using ReportLab
        pdf_content = create_enhanced_pdf(doc, format)
        
        # Return the PDF
        frappe.local.response.filename = f"{doc.name}.pdf"
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"
        
    except Exception as e:
        frappe.logger().error(f"Enhanced PDF generation failed: {e}")
        # Fallback to original method
        return download_pdf(doctype, name, format, doc, no_letterhead, language, letterhead)

def create_enhanced_pdf(doc, format_name=None):
    """Create enhanced PDF with proper invoice formatting"""
    
    from reportlab.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.units import inch
    import io
    
    buffer = io.BytesIO()
    pdf_doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Enhanced styles
    title_style = ParagraphStyle(
        'EnhancedTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=30,
        borderWidth=2,
        borderColor=colors.darkblue,
        borderPadding=10
    )
    
    header_style = ParagraphStyle(
        'EnhancedHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkred,
        spaceBefore=15,
        spaceAfter=10
    )
    
    # Title with document type and number
    story.append(Paragraph(f"🧾 {doc.doctype.upper()}", title_style))
    story.append(Paragraph(f"#{doc.name}", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Company header if available
    if hasattr(doc, 'company') and doc.company:
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkgreen,
            alignment=TA_CENTER,
            spaceAfter=15
        )
        story.append(Paragraph(f"🏢 {doc.company}", company_style))
    
    # Document information section
    story.append(Paragraph("📋 Document Information", header_style))
    
    info_data = []
    if hasattr(doc, 'customer') and doc.customer:
        info_data.append(['👤 Customer:', doc.customer])
    if hasattr(doc, 'supplier') and doc.supplier:
        info_data.append(['🏪 Supplier:', doc.supplier])
    if hasattr(doc, 'posting_date') and doc.posting_date:
        info_data.append(['📅 Date:', str(doc.posting_date)])
    if hasattr(doc, 'due_date') and doc.due_date:
        info_data.append(['⏰ Due Date:', str(doc.due_date)])
    if hasattr(doc, 'status') and doc.status:
        info_data.append(['📊 Status:', doc.status])
    
    if info_data:
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 1, colors.blue),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 25))
    
    # Items section for invoices/orders
    if hasattr(doc, 'items') and doc.items:
        story.append(Paragraph("🛒 Items", header_style))
        
        items_data = [['#', '📦 Item', '🔢 Qty', '💰 Rate', '💵 Amount']]
        
        for idx, item in enumerate(doc.items, 1):
            items_data.append([
                str(idx),
                item.item_name or item.item_code or 'Item',
                str(getattr(item, 'qty', 1)),
                f"${getattr(item, 'rate', 0):.2f}",
                f"${getattr(item, 'amount', 0):.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0,0), (-1,0), colors.darkred),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 15),
            
            # Data styling
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightcyan]),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 25))
    
    # Totals section
    if any(hasattr(doc, field) for field in ['total', 'grand_total', 'total_taxes_and_charges']):
        story.append(Paragraph("💰 Totals", header_style))
        
        totals_data = []
        if hasattr(doc, 'total') and doc.total:
            totals_data.append(['Subtotal:', f"${doc.total:.2f}"])
        if hasattr(doc, 'total_taxes_and_charges') and doc.total_taxes_and_charges:
            totals_data.append(['Taxes & Charges:', f"${doc.total_taxes_and_charges:.2f}"])
        if hasattr(doc, 'discount_amount') and doc.discount_amount:
            totals_data.append(['Discount:', f"-${doc.discount_amount:.2f}"])
        if hasattr(doc, 'grand_total') and doc.grand_total:
            totals_data.append(['🎯 GRAND TOTAL:', f"${doc.grand_total:.2f}"])
        
        if totals_data:
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgreen),
                ('FONTSIZE', (0,-1), (-1,-1), 14),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(totals_table)
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("🚀 Generated with ERPNext + ReportLab Engine", footer_style))
    story.append(Paragraph(f"📅 Generated on: {frappe.utils.now()}", footer_style))
    
    # Build PDF
    pdf_doc.build(story)
    return buffer.getvalue()

def install_enhanced_print_handler():
    """Install enhanced print handler"""
    
    # Override the download_pdf method
    import frappe.utils.print_format
    frappe.utils.print_format.download_pdf = enhanced_download_pdf
    
    frappe.logger().info("✅ Enhanced print handler installed!")
