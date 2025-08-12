import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Create custom fields after app installation"""
    create_print_format_custom_fields()
    create_print_settings_custom_fields()

def create_print_format_custom_fields():
    """Add custom fields to Print Format"""
    
    custom_fields = {
        "Print Format": [
            {
                "fieldname": "pdf_engine_section",
                "fieldtype": "Section Break",
                "label": "PDF Engine Configuration",
                "insert_after": "css",
                "collapsible": 1
            },
            {
                "fieldname": "pdf_engine",
                "fieldtype": "Select",
                "label": "PDF Engine",
                "options": "Auto\nReportLab\nwkhtmltopdf",
                "default": "Auto",
                "insert_after": "pdf_engine_section",
                "description": "Choose PDF generation engine"
            },
            {
                "fieldname": "reportlab_template_link",
                "fieldtype": "Link",
                "label": "ReportLab Template",
                "options": "ReportLab Template",
                "insert_after": "pdf_engine",
                "depends_on": "eval:doc.pdf_engine == 'ReportLab'"
            },
            {
                "fieldname": "column_break_pdf",
                "fieldtype": "Column Break",
                "insert_after": "reportlab_template_link"
            },
            {
                "fieldname": "performance_priority",
                "fieldtype": "Select",
                "label": "Performance Priority",
                "options": "Speed\nQuality\nBalanced",
                "default": "Balanced",
                "insert_after": "column_break_pdf"
            },
            {
                "fieldname": "enable_reportlab_fallback",
                "fieldtype": "Check",
                "label": "Enable Fallback to wkhtmltopdf",
                "default": "1",
                "insert_after": "performance_priority"
            },
            {
                "fieldname": "reportlab_configuration_section",
                "fieldtype": "Section Break",
                "label": "ReportLab Configuration",
                "insert_after": "enable_reportlab_fallback",
                "depends_on": "eval:doc.pdf_engine == 'ReportLab'",
                "collapsible": 1
            },
            {
                "fieldname": "reportlab_config",
                "fieldtype": "JSON",
                "label": "ReportLab Configuration",
                "insert_after": "reportlab_configuration_section",
                "description": "Advanced ReportLab configuration"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)

def create_print_settings_custom_fields():
    """Add custom fields to Print Settings"""
    
    custom_fields = {
        "Print Settings": [
            {
                "fieldname": "pdf_engine_settings",
                "fieldtype": "Section Break",
                "label": "PDF Engine Settings",
                "insert_after": "send_print_as_pdf"
            },
            {
                "fieldname": "default_pdf_engine",
                "fieldtype": "Select",
                "label": "Default PDF Engine",
                "options": "Auto\nReportLab\nwkhtmltopdf",
                "default": "Auto",
                "insert_after": "pdf_engine_settings"
            },
            {
                "fieldname": "enable_reportlab",
                "fieldtype": "Check",
                "label": "Enable ReportLab Engine",
                "default": "1",
                "insert_after": "default_pdf_engine"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)