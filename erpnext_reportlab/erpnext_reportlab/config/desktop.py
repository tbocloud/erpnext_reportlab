from frappe import _

def get_data():
    return [
        {
            "module_name": "ERPNext ReportLab",
            "color": "red",
            "icon": "octicon octicon-file-pdf",
            "type": "module",
            "label": _("PDF Engine"),
            "description": _("Advanced PDF generation with ReportLab")
        }
    ]