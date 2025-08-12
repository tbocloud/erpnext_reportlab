import frappe
from frappe.printing.doctype.print_format.print_format import PrintFormat

class PrintFormatOverride(PrintFormat):
    """Extended Print Format with ReportLab support"""
    
    def validate(self):
        """Enhanced validation with ReportLab checks"""
        super().validate()
        self.validate_reportlab_settings()
    
    def validate_reportlab_settings(self):
        """Validate ReportLab specific settings"""
        if hasattr(self, 'pdf_engine') and self.pdf_engine == 'ReportLab':
            if hasattr(self, 'reportlab_template_link') and self.reportlab_template_link:
                # Check if template exists and is enabled
                if frappe.db.exists("ReportLab Template", self.reportlab_template_link):
                    template = frappe.get_doc("ReportLab Template", self.reportlab_template_link)
                    if not getattr(template, 'enabled', True):
                        frappe.throw(f"ReportLab Template '{self.reportlab_template_link}' is disabled")
    
    def get_pdf_engine(self):
        """Get the preferred PDF engine for this print format"""
        return getattr(self, 'pdf_engine', 'Auto')
    
    def get_reportlab_config(self):
        """Get ReportLab configuration"""
        if hasattr(self, 'reportlab_config') and self.reportlab_config:
            try:
                return frappe.parse_json(self.reportlab_config)
            except:
                return {}
        return {}
    
    def get_performance_priority(self):
        """Get performance priority setting"""
        return getattr(self, 'performance_priority', 'Balanced')
    
    def is_reportlab_fallback_enabled(self):
        """Check if fallback to wkhtmltopdf is enabled"""
        return bool(getattr(self, 'enable_reportlab_fallback', True))