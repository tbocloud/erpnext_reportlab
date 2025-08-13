import frappe
import json
from frappe.model.document import Document

class ReportLabTemplateManager:
    """Manages ReportLab templates and rendering"""
    
    @staticmethod
    def get_template_for_doctype(doctype, print_format=None):
        """Get the best template for a doctype and print format"""
        filters = {
            "enabled": 1,
            "for_doctype": doctype
        }
        
        if print_format:
            filters["for_print_format"] = print_format
        
        # Try to find specific template first
        template = frappe.db.get_value(
            "ReportLab Template", 
            filters,
            ["name", "template_name", "template_type", "template_code", "html_template"],
            order_by="is_default desc, creation desc"
        )
        
        if not template:
            # Fallback to default template for doctype
            template = frappe.db.get_value(
                "ReportLab Template",
                {"enabled": 1, "for_doctype": doctype, "is_default": 1},
                ["name", "template_name", "template_type", "template_code", "html_template"]
            )
        
        if not template:
            # Final fallback to any enabled template
            template = frappe.db.get_value(
                "ReportLab Template",
                {"enabled": 1},
                ["name", "template_name", "template_type", "template_code", "html_template"]
            )
        
        return template
    
    @staticmethod
    def create_default_invoice_template():
        """Create default Sales Invoice template"""
        try:
            # Check if template already exists
            if frappe.db.exists("ReportLab Template", {"template_name": "Default Sales Invoice"}):
                return frappe.get_doc("ReportLab Template", {"template_name": "Default Sales Invoice"})
            
            template_code = '''
def generate_pdf(doc, html, options=None, output=None):
    """Generate Professional Invoice PDF using ReportLab"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, blue
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    import io
    
    buffer = io.BytesIO()
    
    # Create PDF document
    pdf_doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.darkblue,
        spaceAfter=20,
        alignment=1
    )
    
    story = []
    
    # Company Header (Dynamic from doc)
    company_name = getattr(doc, 'company', 'YOUR COMPANY NAME')
    story.append(Paragraph(company_name, title_style))
    story.append(Paragraph("Professional Invoice Services", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Invoice Title (Dynamic)
    invoice_title = f"SALES INVOICE #{getattr(doc, 'name', 'N/A')}"
    story.append(Paragraph(invoice_title, styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Customer and Invoice Details (Dynamic)
    customer = getattr(doc, 'customer_name', 'N/A')
    posting_date = getattr(doc, 'posting_date', 'N/A')
    due_date = getattr(doc, 'due_date', 'N/A')
    status = getattr(doc, 'status', 'N/A')
    grand_total = getattr(doc, 'grand_total', 0)
    
    details_data = [
        ["Bill To:", "Invoice Details:"],
        [customer, f"Invoice Number: {doc.name}"],
        ["Customer Address", f"Date: {posting_date}"],
        ["City, State ZIP", f"Due Date: {due_date}"],
        ["", f"Status: {status}"],
        ["", "Payment Terms: Net 30 Days"]
    ]
    
    details_table = Table(details_data, colWidths=[3*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 30))
    
    # Items Section (Dynamic from doc.items)
    story.append(Paragraph("INVOICE ITEMS", styles['Heading2']))
    story.append(Spacer(1, 15))
    
    # Dynamic items table
    items_data = [["#", "Description", "Qty", "Unit Price", "Line Total"]]
    
    if hasattr(doc, 'items'):
        for idx, item in enumerate(doc.items, 1):
            items_data.append([
                str(idx),
                getattr(item, 'item_name', '') or getattr(item, 'description', ''),
                str(getattr(item, 'qty', 0)),
                f"${getattr(item, 'rate', 0):,.2f}",
                f"${getattr(item, 'amount', 0):,.2f}"
            ])
    
    # Add totals
    items_data.extend([
        ["", "", "", "Subtotal:", f"${grand_total:,.2f}"],
        ["", "", "", "Tax:", "$0.00"],
        ["", "", "", "TOTAL:", f"${grand_total:,.2f}"]
    ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('ALIGN', (0, 1), (0, -4), 'CENTER'),
        ('ALIGN', (1, 1), (1, -4), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -4), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 9),
        
        # Totals
        ('FONTNAME', (3, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (3, -3), (-1, -1), colors.lightgrey),
        ('ALIGN', (3, -3), (-1, -1), 'RIGHT'),
        
        # Final total
        ('BACKGROUND', (3, -1), (-1, -1), colors.darkblue),
        ('TEXTCOLOR', (3, -1), (-1, -1), colors.white),
        
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
        ('GRID', (3, -3), (-1, -1), 1, colors.black),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_text = f"""
    <b>Payment Information:</b><br/>
    Invoice generated on {posting_date}<br/>
    Thank you for your business!<br/><br/>
    <i>Generated using ERPNext ReportLab Engine</i>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    pdf_doc.build(story)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data
'''

            template_doc = frappe.get_doc({
                "doctype": "ReportLab Template",
                "template_name": "Default Sales Invoice",
                "enabled": 1,
                "template_type": "Pure ReportLab",
                "for_doctype": "Sales Invoice",
                "is_default": 1,
                "template_code": template_code,
                "description": "Default professional Sales Invoice template with dynamic content"
            })
            
            template_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            print("✅ Created Default Sales Invoice template")
            return template_doc
            
        except Exception as e:
            print(f"❌ Error creating template: {str(e)}")
            return None

def get_template_based_pdf_generator(html, options=None, output=None):
    """Dynamic PDF generator that uses ReportLab templates"""
    try:
        # Get document context
        doctype = options.get('doctype') if options else None
        docname = options.get('docname') if options else None
        print_format = options.get('print_format') if options else None
        
        if not doctype or not docname:
            # Fallback to static generator
            return static_pdf_generator(html, options, output)
        
        # Get the document
        doc = frappe.get_doc(doctype, docname)
        
        # Get appropriate template
        template_data = ReportLabTemplateManager.get_template_for_doctype(doctype, print_format)
        
        if not template_data:
            # Create default template if none exists
            if doctype == "Sales Invoice":
                ReportLabTemplateManager.create_default_invoice_template()
                template_data = ReportLabTemplateManager.get_template_for_doctype(doctype, print_format)
        
        if template_data and template_data[3]:  # template_code exists
            # Execute the template code
            template_globals = {
                'doc': doc,
                'html': html,
                'options': options,
                'output': output,
                'frappe': frappe
            }
            
            exec(template_data[3], template_globals)
            
            if 'generate_pdf' in template_globals:
                pdf_data = template_globals['generate_pdf'](doc, html, options, output)
                print(f"✅ Generated PDF using template: {template_data[1]}")
                return pdf_data
        
        # Fallback to static generator
        return static_pdf_generator(html, options, output)
        
    except Exception as e:
        print(f"❌ Template-based PDF generation error: {str(e)}")
        # Fallback to static generator
        return static_pdf_generator(html, options, output)

def static_pdf_generator(html, options=None, output=None):
    """Fallback static PDF generator"""
    # Your existing enhanced_pdf_generator code here
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.lib.colors import black, blue
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("FALLBACK PDF GENERATOR", styles['Title']))
        story.append(Paragraph("Template-based generation failed, using static fallback.", styles['Normal']))
        
        doc.build(story)
        return buffer.getvalue()
        
    except Exception as e:
        return f"PDF Generation Error: {str(e)}".encode()
