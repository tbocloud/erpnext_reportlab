import frappe
import json

def execute():
    """Fix PDF Engine Configuration JSON constraints"""
    try:
        # Get all PDF Engine Configuration records
        records = frappe.get_all("PDF Engine Configuration", fields=["name"])
        
        for record in records:
            doc = frappe.get_doc("PDF Engine Configuration", record.name)
            
            # Fix engine_configuration - this is the only JSON field that exists
            if not doc.engine_configuration or doc.engine_configuration == "null":
                doc.engine_configuration = json.dumps({
                    "quality": "high",
                    "page_size": "A4",
                    "orientation": "portrait"
                })
            
            # Save without validation first
            doc.db_update()
        
        frappe.db.commit()
        print("✅ Fixed PDF Engine Configuration JSON constraints")
        
    except Exception as e:
        print(f"❌ Error fixing JSON constraints: {str(e)}")
        frappe.db.rollback()
