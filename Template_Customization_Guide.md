# 🎯 **ReportLab Template System - User Guide**

## ✅ **What We Just Created:**

You now have a **dynamic template system** instead of static hardcoded PDF formats! Here's what changed:

### 🔄 **Before (Static):**
- ❌ **Hardcoded** PDF layout in code
- ❌ **No customization** through UI
- ❌ **Fixed content** - same for all documents

### ✅ **After (Dynamic Templates):**
- ✅ **Database-driven** templates
- ✅ **UI customization** through ERPNext
- ✅ **Dynamic content** - uses real document data

---

## 🎨 **How to Customize Your PDF Templates:**

### **Step 1: Access Templates**
1. Go to ERPNext → **Setup** → **ReportLab Template**
2. You'll see: **"Default Sales Invoice"** template

### **Step 2: Edit Template**
1. Click on **"Default Sales Invoice"**
2. Scroll to **Template Code** field
3. **Modify the code** to customize your PDF

### **Step 3: Key Customization Points**

#### **🏢 Company Information:**
```python
# Change this line:
company_name = getattr(doc, 'company', 'YOUR COMPANY NAME')

# To:
company_name = getattr(doc, 'company', 'My Business Inc.')
```

#### **🎨 Colors & Styling:**
```python
# Header color (currently blue):
textColor=colors.darkblue

# Change to red:
textColor=colors.red

# Or custom color:
from reportlab.lib.colors import Color
custom_color = Color(0.2, 0.4, 0.8)  # RGB values
```

#### **📊 Table Styling:**
```python
# Header background (currently dark blue):
('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),

# Change to green:
('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
```

### **Step 4: Logo Addition:**
```python
# Add after story = []:
from reportlab.platypus import Image
logo = Image('/path/to/your/logo.png', width=2*inch, height=1*inch)
story.append(logo)
story.append(Spacer(1, 20))
```

---

## 🎯 **Template Types You Can Create:**

### **1. Sales Invoice Templates:**
- Customer invoices
- Professional service bills
- Product sales receipts

### **2. Purchase Order Templates:**
- Vendor orders
- Procurement documents
- Supply requests

### **3. Custom Document Templates:**
- Quotations
- Delivery notes
- Payment receipts

---

## 📝 **Creating New Templates:**

### **Step 1: Create New Template**
1. Go to **Setup** → **ReportLab Template** → **New**
2. Fill details:
   - **Template Name**: "Modern Sales Invoice"
   - **For Doctype**: "Sales Invoice"
   - **Template Type**: "Pure ReportLab"
   - **Is Default**: Check if this should be primary

### **Step 2: Template Code Structure:**
```python
def generate_pdf(doc, html, options=None, output=None):
    """Your custom PDF generator"""
    # Import ReportLab modules
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    # ... other imports
    
    # Access document data:
    invoice_number = doc.name
    customer_name = doc.customer_name
    total_amount = doc.grand_total
    
    # Build your PDF layout
    story = []
    story.append(Paragraph(f"Invoice: {invoice_number}", styles['Title']))
    
    # Return PDF data
    return buffer.getvalue()
```

---

## 🔧 **Available Document Fields:**

### **Sales Invoice (doc.fieldname):**
- `doc.name` - Invoice number
- `doc.customer_name` - Customer name
- `doc.company` - Your company
- `doc.posting_date` - Invoice date
- `doc.due_date` - Payment due date
- `doc.grand_total` - Total amount
- `doc.status` - Invoice status
- `doc.items` - List of invoice items

### **Each Item (item.fieldname):**
- `item.item_name` - Product/service name
- `item.qty` - Quantity
- `item.rate` - Unit price
- `item.amount` - Line total
- `item.description` - Item description

---

## 🎨 **Styling Examples:**

### **Professional Blue Theme:**
```python
title_color = colors.darkblue
header_bg = colors.lightblue
accent_color = colors.blue
```

### **Corporate Green Theme:**
```python
title_color = colors.darkgreen
header_bg = colors.lightgreen
accent_color = colors.green
```

### **Modern Purple Theme:**
```python
from reportlab.lib.colors import Color
title_color = Color(0.4, 0.2, 0.8)  # Purple
header_bg = Color(0.9, 0.9, 1.0)    # Light purple
```

---

## 🚀 **Testing Your Templates:**

### **Method 1: Through ERPNext**
1. Go to any **Sales Invoice**
2. Click **Print** → **PDF**
3. Your template will be used automatically

### **Method 2: Preview in Template**
1. Edit your template
2. Add test data in **Test Data** field
3. Use **Preview** feature (if available)

---

## 🛠 **Template Priority System:**

1. **Specific Template** - For doctype + print format
2. **Default Template** - For doctype (is_default=1)
3. **Any Enabled Template** - Fallback
4. **Static Generator** - Final fallback

---

## 📚 **Advanced Customizations:**

### **Conditional Content:**
```python
if doc.status == "Paid":
    story.append(Paragraph("✅ PAID", paid_style))
else:
    story.append(Paragraph("⏳ PENDING", pending_style))
```

### **Multi-Page Support:**
```python
# Add page breaks
from reportlab.platypus import PageBreak
story.append(PageBreak())
```

### **Charts & Graphs:**
```python
from reportlab.graphics.charts.piecharts import Pie
# Add charts to your PDFs
```

---

## 🎯 **Your Next Steps:**

1. **Try Editing** the "Default Sales Invoice" template
2. **Change Colors** to match your brand
3. **Add Your Logo** and company details
4. **Create New Templates** for other document types
5. **Test Different Styles** to find what works best

## 💡 **Need Help?**
- Templates are stored in **ReportLab Template** doctype
- Code editor has **syntax highlighting**
- **Save & Test** frequently while customizing
- **Backup** your templates before major changes

**🎉 You now have full control over your PDF layouts!**
