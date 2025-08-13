import frappe
import json
import os

def install_print_settings_custom_fields():
    """Install custom fields for Print Settings"""
    try:
        # Get the fixtures file path
        fixtures_path = os.path.join(
            frappe.get_app_path("erpnext_reportlab"), 
            "erpnext_reportlab",
            "fixtures", 
            "print_settings_custom_fields.json"
        )
        
        # Read the custom fields data
        with open(fixtures_path, 'r') as f:
            custom_fields = json.load(f)
        
        for field_data in custom_fields:
            # Check if the custom field already exists
            existing_field = frappe.db.exists("Custom Field", {
                "dt": field_data["dt"],
                "fieldname": field_data["fieldname"]
            })
            
            if not existing_field:
                # Create the custom field
                custom_field = frappe.get_doc(field_data)
                custom_field.insert(ignore_permissions=True)
                print(f"Created custom field: {field_data['fieldname']}")
            else:
                print(f"Custom field already exists: {field_data['fieldname']}")
        
        frappe.db.commit()
        print("✅ Print Settings custom fields installed successfully!")
        
        # Clear cache to reload the form
        frappe.clear_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ Error installing custom fields: {str(e)}")
        frappe.db.rollback()
        return False

def uninstall_print_settings_custom_fields():
    """Remove custom fields from Print Settings"""
    try:
        fieldnames = [
            "reportlab_section",
            "default_pdf_engine", 
            "enable_reportlab",
            "pdf_performance_monitoring",
            "reportlab_quality",
            "auto_template_selection"
        ]
        
        for fieldname in fieldnames:
            existing_field = frappe.db.exists("Custom Field", {
                "dt": "Print Settings",
                "fieldname": fieldname
            })
            
            if existing_field:
                frappe.delete_doc("Custom Field", existing_field, ignore_permissions=True)
                print(f"Removed custom field: {fieldname}")
        
        frappe.db.commit()
        print("✅ Print Settings custom fields removed successfully!")
        frappe.clear_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing custom fields: {str(e)}")
        frappe.db.rollback()
        return False

def configure_reportlab_settings():
    """Configure Print Settings to use ReportLab by default"""
    try:
        print_settings = frappe.get_single("Print Settings")
        
        # Set ReportLab as default
        if hasattr(print_settings, 'default_pdf_engine'):
            print_settings.default_pdf_engine = "ReportLab"
        if hasattr(print_settings, 'enable_reportlab'):
            print_settings.enable_reportlab = 1
        if hasattr(print_settings, 'pdf_performance_monitoring'):
            print_settings.pdf_performance_monitoring = 1
        if hasattr(print_settings, 'reportlab_quality'):
            print_settings.reportlab_quality = "High"
        if hasattr(print_settings, 'auto_template_selection'):
            print_settings.auto_template_selection = 1
            
        print_settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Print Settings configured for ReportLab!")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring settings: {str(e)}")
        return False

# Install when module is imported
if __name__ == "__main__":
    install_print_settings_custom_fields()
    configure_reportlab_settings()
