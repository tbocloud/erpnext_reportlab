#!/usr/bin/env python3

import frappe
import sys
import os

def install_default_templates():
    """Install default ReportLab templates"""
    try:
        # Initialize Frappe context
        frappe.init_site("extra.com")
        frappe.connect()
        
        from erpnext_reportlab.erpnext_reportlab.utils.template_manager import ReportLabTemplateManager
        
        print("🔧 Installing default ReportLab templates...")
        
        # Create default Sales Invoice template
        template = ReportLabTemplateManager.create_default_invoice_template()
        if template:
            print(f"✅ Created template: {template.template_name}")
        
        print("✅ Default templates installed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error installing templates: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            frappe.destroy()
        except:
            pass

def test_template_system():
    """Test the template system"""
    try:
        frappe.init_site("extra.com")
        frappe.connect()
        
        from erpnext_reportlab.erpnext_reportlab.utils.template_manager import ReportLabTemplateManager
        
        print("🧪 Testing template system...")
        
        # Test getting template for Sales Invoice
        template = ReportLabTemplateManager.get_template_for_doctype("Sales Invoice")
        
        if template:
            print(f"✅ Found template: {template[1]} for Sales Invoice")
            print(f"   Template Type: {template[2]}")
            print(f"   Has Code: {'Yes' if template[3] else 'No'}")
            return True
        else:
            print("❌ No template found for Sales Invoice")
            return False
            
    except Exception as e:
        print(f"❌ Template test error: {str(e)}")
        return False
    finally:
        try:
            frappe.destroy()
        except:
            pass

def list_templates():
    """List all available templates"""
    try:
        frappe.init_site("extra.com")
        frappe.connect()
        
        templates = frappe.get_all("ReportLab Template", 
                                  fields=["name", "template_name", "for_doctype", "enabled", "is_default"],
                                  order_by="for_doctype, is_default desc")
        
        print("📋 Available ReportLab Templates:")
        print("-" * 80)
        for template in templates:
            status = "✅ Enabled" if template.enabled else "❌ Disabled"
            default = " (DEFAULT)" if template.is_default else ""
            print(f"• {template.template_name}{default}")
            print(f"  For: {template.for_doctype} | Status: {status}")
            print(f"  ID: {template.name}")
            print()
        
        if not templates:
            print("No templates found. Run with --install to create default templates.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing templates: {str(e)}")
        return False
    finally:
        try:
            frappe.destroy()
        except:
            pass

def create_template_guide():
    """Create a template creation guide"""
    guide = """
# 📝 ReportLab Template Creation Guide

## How to Create Custom Templates

### 1. Through ERPNext UI:
1. Go to: **Setup → ReportLab Template**
2. Click **New**
3. Fill in the details:
   - **Template Name**: Descriptive name (e.g., "Modern Sales Invoice")
   - **For Doctype**: Sales Invoice, Purchase Order, etc.
   - **Template Type**: "Pure ReportLab" or "HTML + ReportLab"
   - **Is Default**: Check if this should be the default template
   - **Enabled**: Check to activate

### 2. Template Code Structure:
```python
def generate_pdf(doc, html, options=None, output=None):
    \"\"\"Generate PDF for document\"\"\"
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    
    buffer = io.BytesIO()
    pdf_doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    
    # Use doc.field_name to access document data
    company_name = getattr(doc, 'company', 'Company Name')
    customer_name = getattr(doc, 'customer_name', 'Customer')
    
    story.append(Paragraph(f"Invoice from {company_name}", styles['Title']))
    story.append(Paragraph(f"Bill To: {customer_name}", styles['Normal']))
    
    # Add items table
    if hasattr(doc, 'items'):
        for item in doc.items:
            story.append(Paragraph(f"Item: {item.item_name}", styles['Normal']))
    
    pdf_doc.build(story)
    return buffer.getvalue()
```

### 3. Available Document Fields:
**Sales Invoice:**
- doc.name (Invoice number)
- doc.customer_name
- doc.company
- doc.posting_date
- doc.due_date
- doc.grand_total
- doc.items (list of items)

**Each Item:**
- item.item_name
- item.qty
- item.rate
- item.amount

### 4. Customization Examples:

**Change Colors:**
```python
from reportlab.lib import colors
title_style.textColor = colors.red  # Red title
```

**Custom Table Styling:**
```python
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.blue),  # Blue header
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),   # White text
]))
```

**Add Company Logo:**
```python
from reportlab.platypus import Image
logo = Image('/path/to/logo.png', width=2*inch, height=1*inch)
story.append(logo)
```

### 5. Testing Templates:
- Create template in UI
- Generate PDF from Sales Invoice
- Check for errors in console
- Adjust template code as needed

### 6. Template Priority:
1. Specific template for doctype + print format
2. Default template for doctype
3. Any enabled template
4. Fallback to static generator

## Template Management Commands:
```bash
# Install default templates
python template_installer.py --install

# Test template system
python template_installer.py --test

# List all templates
python template_installer.py --list
```
"""
    
    try:
        with open("ReportLab_Template_Guide.md", "w") as f:
            f.write(guide)
        print("✅ Template creation guide saved to: ReportLab_Template_Guide.md")
        return True
    except Exception as e:
        print(f"❌ Error creating guide: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("📋 ReportLab Template Manager")
        print("\nUsage:")
        print("  python template_installer.py --install   # Install default templates")
        print("  python template_installer.py --test      # Test template system")
        print("  python template_installer.py --list      # List all templates")
        print("  python template_installer.py --guide     # Create template guide")
        return
    
    command = sys.argv[1]
    
    if command == "--install":
        success = install_default_templates()
        if success:
            print("\n🎉 Installation complete! You can now:")
            print("1. Go to Setup → ReportLab Template to view templates")
            print("2. Create new Sales Invoice to test PDF generation")
            print("3. Customize templates through the UI")
    
    elif command == "--test":
        test_template_system()
    
    elif command == "--list":
        list_templates()
    
    elif command == "--guide":
        create_template_guide()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use --install, --test, --list, or --guide")

if __name__ == "__main__":
    main()
