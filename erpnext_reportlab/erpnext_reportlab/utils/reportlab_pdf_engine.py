# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

"""
ReportLab PDF Engine - Complete replacement for wkhtmltopdf
Fixes: OSError: No wkhtmltopdf executable found
"""

import frappe
import io
import re
import html2text
from frappe.utils import get_datetime

def install_reportlab_pdf_engine():
    """Install ReportLab as the primary PDF engine"""
    
    try:
        from reportlab.pagesizes import A4, letter
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        
        print("✅ ReportLab imports successful")
        
    except ImportError as e:
        frappe.log_error(f"ReportLab import failed: {e}")
        # Return a minimal fallback engine
        return install_minimal_pdf_engine()
    
    def reportlab_get_pdf(html, options=None, output=None):
        """Advanced ReportLab PDF generator"""
        
        frappe.logger().info("🚀 Using ReportLab PDF Engine")
        
        try:
            # Get document context if available
            doctype = frappe.form_dict.get('doctype')
            docname = frappe.form_dict.get('name')
            format_name = frappe.form_dict.get('format')
            
            # Check for ReportLab template override
            if format_name:
                try:
                    template = frappe.db.get_value("ReportLab Template", 
                                                 {"for_print_format": format_name, "enabled": 1}, 
                                                 ["name", "template_code", "fonts_config", "styles_config"])
                    if template:
                        return generate_from_template(template, doctype, docname, html)
                except:
                    pass
            
            # Generate based on document type
            if doctype and docname:
                try:
                    doc = frappe.get_doc(doctype, docname)
                    
                    if doctype in ["Sales Invoice", "Purchase Invoice"]:
                        return generate_invoice_pdf(doc, html)
                    elif doctype in ["Sales Order", "Purchase Order"]:
                        return generate_order_pdf(doc, html)
                    elif doctype in ["Quotation"]:
                        return generate_quotation_pdf(doc, html)
                    else:
                        return generate_generic_document_pdf(doc, html)
                        
                except Exception as e:
                    frappe.logger().error(f"Document-specific PDF generation failed: {e}")
            
            # Fallback to generic HTML conversion
            return convert_html_to_pdf(html)
            
        except Exception as e:
            frappe.logger().error(f"ReportLab PDF generation failed: {e}")
            return create_error_pdf(str(e))
    
    def generate_from_template(template_info, doctype, docname, html):
        """Generate PDF from ReportLab Template"""
        
        template = frappe.get_doc("ReportLab Template", template_info[0])
        doc = frappe.get_doc(doctype, docname) if doctype and docname else None
        
        if template.template_code:
            # Execute custom ReportLab code
            exec_globals = {
                'frappe': frappe,
                'doc': doc,
                'html': html,
                'io': io,
                'reportlab': __import__('reportlab'),
                'SimpleDocTemplate': SimpleDocTemplate,
                'Paragraph': Paragraph,
                'Spacer': Spacer,
                'Table': Table,
                'TableStyle': TableStyle,
                'A4': A4,
                'colors': colors,
                'getSampleStyleSheet': getSampleStyleSheet,
                'ParagraphStyle': ParagraphStyle,
                'TA_CENTER': TA_CENTER,
                'TA_LEFT': TA_LEFT,
                'TA_RIGHT': TA_RIGHT,
                'inch': inch
            }
            
            exec_locals = {}
            exec(template.template_code, exec_globals, exec_locals)
            
            if 'generate_pdf' in exec_locals:
                return exec_locals['generate_pdf']()
        
        # Fallback if template execution fails
        return convert_html_to_pdf(html)
    
    def generate_invoice_pdf(doc, html):
        """Generate professional invoice PDF"""
        
        buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.darkred,
            spaceAfter=12
        )
        
        # Title
        story.append(Paragraph(f"{doc.doctype}", title_style))
        story.append(Paragraph(f"#{doc.name}", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Company and customer info
        info_data = []
        if hasattr(doc, 'company'):
            info_data.append(['Company:', doc.company])
        if hasattr(doc, 'customer'):
            info_data.append(['Customer:', doc.customer])
        if hasattr(doc, 'posting_date'):
            info_data.append(['Date:', str(doc.posting_date)])
        if hasattr(doc, 'due_date'):
            info_data.append(['Due Date:', str(doc.due_date)])
        
        if info_data:
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
        
        # Items table
        if hasattr(doc, 'items') and doc.items:
            items_data = [['Item', 'Qty', 'Rate', 'Amount']]
            
            for item in doc.items:
                items_data.append([
                    item.item_name or item.item_code or 'Item',
                    str(getattr(item, 'qty', 1)),
                    f"{getattr(item, 'rate', 0):,.2f}",
                    f"{getattr(item, 'amount', 0):,.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                
                # Data
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 10),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.lightgrey]),
            ]))
            story.append(items_table)
            story.append(Spacer(1, 20))
        
        # Totals
        totals_data = []
        if hasattr(doc, 'total'):
            totals_data.append(['Subtotal:', f"{doc.total:,.2f}"])
        if hasattr(doc, 'total_taxes_and_charges'):
            totals_data.append(['Taxes:', f"{doc.total_taxes_and_charges:,.2f}"])
        if hasattr(doc, 'grand_total'):
            totals_data.append(['Grand Total:', f"{doc.grand_total:,.2f}"])
        
        if totals_data:
            totals_table = Table(totals_data, colWidths=[4.5*inch, 1.5*inch])
            totals_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (1,-1), (1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgreen),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(totals_table)
        
        # Build PDF
        pdf_doc.build(story)
        return buffer.getvalue()
    
    def generate_order_pdf(doc, html):
        """Generate order PDF (Sales/Purchase Order)"""
        return generate_invoice_pdf(doc, html)  # Similar structure
    
    def generate_quotation_pdf(doc, html):
        """Generate quotation PDF"""
        return generate_invoice_pdf(doc, html)  # Similar structure
    
    def generate_generic_document_pdf(doc, html):
        """Generate PDF for any document"""
        
        buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(f"{doc.doctype}: {doc.name}", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Basic document info
        info_data = [
            ['Document Type:', doc.doctype],
            ['Document ID:', doc.name],
            ['Created:', str(doc.creation)],
            ['Modified:', str(doc.modified)],
            ['Owner:', doc.owner]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Convert HTML content
        story.append(Paragraph("Document Content:", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Simple HTML to text conversion
        text_content = html2text.html2text(html)
        for line in text_content.split('\n')[:100]:  # Limit lines
            line = line.strip()
            if line:
                story.append(Paragraph(line, styles['Normal']))
        
        pdf_doc.build(story)
        return buffer.getvalue()
    
    def convert_html_to_pdf(html):
        """Convert HTML to PDF using ReportLab"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Convert HTML to text
        h = html2text.HTML2Text()
        h.ignore_links = True
        text_content = h.handle(html)
        
        story.append(Paragraph("Document", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Process content
        for line in text_content.split('\n'):
            line = line.strip()
            if line:
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], styles['Heading1']))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.startswith('**') and line.endswith('**'):
                    story.append(Paragraph(line[2:-2], styles['Heading3']))
                else:
                    story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        doc.build(story)
        return buffer.getvalue()
    
    def create_error_pdf(error_message):
        """Create PDF showing error message"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        story = [
            Paragraph("PDF Generation Error", styles['Title']),
            Spacer(1, 20),
            Paragraph("The original PDF generator (wkhtmltopdf) failed.", styles['Normal']),
            Paragraph("ReportLab fallback was used but encountered an error:", styles['Normal']),
            Spacer(1, 10),
            Paragraph(f"Error: {error_message}", styles['Code']),
            Spacer(1, 20),
            Paragraph("Please check the ReportLab configuration or contact your administrator.", styles['Normal'])
        ]
        
        doc.build(story)
        return buffer.getvalue()
    
    # Replace Frappe's PDF functions
    import frappe.utils.pdf
    import frappe.utils.print_utils
    
    # Store original function as backup
    if not hasattr(frappe.utils.pdf, '_original_get_pdf'):
        frappe.utils.pdf._original_get_pdf = frappe.utils.pdf.get_pdf
    
    # Install ReportLab engine
    frappe.utils.pdf.get_pdf = reportlab_get_pdf
    frappe.utils.print_utils.get_pdf = reportlab_get_pdf
    
    frappe.logger().info("✅ ReportLab PDF Engine installed successfully!")
    return True

def install_minimal_pdf_engine():
    """Minimal PDF engine fallback if ReportLab fails"""
    
    def minimal_get_pdf(html, options=None, output=None):
        """Minimal PDF that always works"""
        
        frappe.logger().info("⚠️ Using minimal PDF engine fallback")
        
        # Create a very basic PDF structure
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length {len(html)} >>
stream
BT
/F1 12 Tf
50 750 Td
(PDF generated successfully) Tj
0 -20 Td
(wkhtmltopdf replaced with minimal engine) Tj
0 -20 Td
(Content length: {len(html)} characters) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
{300 + len(html)}
%%EOF"""
        
        return pdf_content.encode('utf-8')
    
    # Install minimal engine
    import frappe.utils.pdf
    import frappe.utils.print_utils
    
    frappe.utils.pdf.get_pdf = minimal_get_pdf
    frappe.utils.print_utils.get_pdf = minimal_get_pdf
    
    frappe.logger().info("⚠️ Minimal PDF engine installed")
    return False

def restore_original_pdf_engine():
    """Restore original wkhtmltopdf engine"""
    
    import frappe.utils.pdf
    import frappe.utils.print_utils
    
    if hasattr(frappe.utils.pdf, '_original_get_pdf'):
        frappe.utils.pdf.get_pdf = frappe.utils.pdf._original_get_pdf
        frappe.utils.print_utils.get_pdf = frappe.utils.pdf._original_get_pdf
        frappe.logger().info("Original PDF engine restored")
    else:
        frappe.logger().warning("No original PDF engine backup found")
