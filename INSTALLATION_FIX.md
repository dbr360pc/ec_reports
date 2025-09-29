# Installation Error Fixes

## ❌ Problem 1: Duplicate Box Codes
**Error:** `Box code "731" already exists in another active mapping`

**Root Cause:** Duplicate box codes in the VAT module's data file
- Line 24: Income Tax Withholdings → code "731" ✅ (correct)  
- Line 81: VAT Collected → code "731" ❌ (incorrect, duplicate)

## ❌ Problem 2: Invalid Label Tags  
**Error:** `Label tag must contain a "for". To match label style without corresponding field or button, use 'class="o_form_label"'.`

**Root Cause:** Label tags without proper "for" attribute or "o_form_label" class

## ✅ Solutions Applied

### 1. Fixed Duplicate Box Codes
**File:** `l10n_ec_reports_vat/data/ec_104_line_data.xml`

**Changed:**
```xml
<!-- OLD (duplicate code 731) -->
<field name="name">IVA Causado</field>
<field name="code">731</field>

<!-- NEW (unique code 799) -->
<field name="name">IVA Causado</field>  
<field name="code">799</field>
```

### 2. Updated Wizard Logic
**File:** `l10n_ec_reports_vat/wizards/vat_report_wizard.py`

**Added VAT collected mapping:**
```python
if move_type in ['out_invoice', 'out_refund']:
    codes.append('521')  # Sales VAT (base)
    codes.append('799')  # VAT collected (tax amount)  # ← NEW
```

### 3. Fixed Label Tags in Views
**Files:** 
- `l10n_ec_reports_vat/views/vat_report_wizard_views.xml`
- `l10n_ec_reports_103/views/withholding_report_wizard_views.xml`

**Changed:**
```xml
<!-- OLD (missing required attribute) -->
<label string="Report Generated Successfully"/>

<!-- NEW (with proper class) -->
<label string="Report Generated Successfully" class="o_form_label"/>
```

## 📋 Final Box Code Mapping (Ecuador Form 104)

| Code | Description | Usage |
|------|-------------|--------|
| 521 | Sales VAT (base) | Sales invoice base amounts |
| 522 | Sales 0% VAT | Sales with 0% VAT |
| 523 | Sales no VAT | Sales exempt from VAT |
| 611 | Purchase VAT (base) | Purchase invoice base amounts |
| 612 | Purchase 0% VAT | Purchases with 0% VAT |
| 613 | Purchase no VAT | Purchases exempt from VAT |
| 721 | VAT Ret. Goods | VAT withholding on goods |
| 723 | VAT Ret. Services | VAT withholding on services |
| 731 | Income Tax Ret. | Income tax withholdings |
| 741 | VAT Paid | VAT paid (input credit) |
| 751 | Compensations | Tax compensations |
| 799 | VAT Collected | VAT collected (output tax) |

## 🚀 Ready for Installation  
The modules should now install without errors:

✅ **All box codes are unique** and properly mapped according to Ecuador's Form 104 structure  
✅ **All view elements comply** with Odoo 17 validation requirements  
✅ **Label tags have proper** class attributes for consistent styling  

**Next Steps:**
1. Try installing `l10n_ec_reports_vat` first (base module)
2. Then install `l10n_ec_reports_ats_sri` (depends on VAT module)  
3. Finally install `l10n_ec_reports_103` (depends on VAT module)