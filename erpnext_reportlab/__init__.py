__version__ = "0.0.1"

def install_pdf_fix():
    """Install enhanced PDF generator to replace wkhtmltopdf"""
    try:
        import frappe
        import frappe.utils.pdf
        
        # Import the enhanced generator from the main module
        from erpnext_reportlab.erpnext_reportlab import enhanced_pdf_generator
        
        # Replace the PDF function with our enhanced generator
        frappe.utils.pdf.get_pdf = enhanced_pdf_generator
        print("✅ Enhanced ReportLab PDF generator installed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        pass
    except Exception as e:
        print(f"❌ PDF fix installation failed: {str(e)}")
        pass

# Auto-install on import
try:
    install_pdf_fix()
except Exception as e:
    print(f"❌ Auto-install failed: {str(e)}")
    pass
