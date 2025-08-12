import frappe

def validate_print_format(doc, method):
    """Validate print format on save"""
    # Add any validation logic here
    pass

def on_print_format_update(doc, method):
    """Handle print format updates"""
    # Clear any cached templates or configurations
    if hasattr(doc, 'pdf_engine'):
        frappe.cache().delete_key(f"pdf_engine_config_{doc.name}")