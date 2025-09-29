# Installation Error Fix

## ❌ Problem Identified
**Error:** `Box code "731" already exists in another active mapping`

**Root Cause:** Duplicate box codes in the VAT module's data file
- Line 24: Income Tax Withholdings → code "731" ✅ (correct)  
- Line 81: VAT Collected → code "731" ❌ (incorrect, duplicate)

## ✅ Solution Applied

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
The module should now install without errors. All box codes are unique and properly mapped according to Ecuador's Form 104 structure.