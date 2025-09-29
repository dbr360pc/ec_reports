# Installation and Testing Guide

## Prerequisites

1. **Odoo 17 Community Edition** installed and running
2. **Ecuador Localization** (`l10n_ec`) module installed
3. **Database** with Ecuadorian company setup (RUC, address, etc.)

## Installation Steps

### 1. Copy Modules
```bash
# Copy all three modules to your Odoo addons directory
cp -r l10n_ec_reports_vat /path/to/odoo/addons/
cp -r l10n_ec_reports_ats_sri /path/to/odoo/addons/
cp -r l10n_ec_reports_103 /path/to/odoo/addons/
```

### 2. Update Apps List
- Access Odoo as Administrator
- Go to Apps → Update Apps List
- Search for "Ecuador Reports"

### 3. Install Modules
Install in this order (dependencies):
1. `EC Reports VAT` (base functionality)
2. `EC Reports ATS` (depends on VAT module)
3. `EC Reports 103` (depends on VAT module)

## Initial Setup

### 1. Tax Groups Configuration
Go to **Accounting → Configuration → Tax Groups** and verify:
- VAT groups have correct codes (`vat`, `vat0`, `novat`)
- Withholding groups exist (`ret_vat_b`, `ret_vat_srv`, `ret_ir`)

### 2. Partner Setup
Ensure all suppliers/customers have:
- **VAT/RUC** properly configured
- **ID Type** selected (Cédula, RUC, Pasaporte, etc.)
- **Valid document authorization** for suppliers

## Testing Scenarios

### Test 1: Form 104 VAT Report
1. Go to **Accounting → Reporting → Ecuador Reports → VAT Report**
2. Select current month period
3. Click "Generate Report" 
4. Verify tax amounts by group
5. Export PDF to check format

**Expected Results:**
- Box 521: Sales with VAT >0%
- Box 522: Sales with VAT 0%
- Box 611: Purchases with VAT >0%
- Box 612: Purchases with VAT 0%

### Test 2: ATS XML Generation
1. Go to **Accounting → Reporting → Ecuador Reports → ATS Report**
2. Select month with sales and purchase invoices
3. Run validation (should show any errors)
4. Generate XML and download ZIP file
5. Extract and verify XML structure

**Expected XML Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<iva>
  <TipoIDInformante>R</TipoIDInformante>
  <IdInformante>1234567890001</IdInformante>
  <ventas>
    <detalleVentas>
      <!-- Sales details -->
    </detalleVentas>
  </ventas>
  <compras>
    <detalleCompras>
      <!-- Purchase details -->
    </detalleCompras>
  </compras>
</iva>
```

### Test 3: Form 103 Withholding Report
1. Create purchase invoice with withholding taxes
2. Go to **Accounting → Reporting → Ecuador Reports → Withholding Report**
3. Select period and generate report
4. Verify withholding amounts are properly categorized

**Expected Categories:**
- VAT Withholding - Goods
- VAT Withholding - Services  
- Income Tax Withholding

## Common Issues & Solutions

### Issue 1: No Data in Reports
**Cause:** Invoices not in 'posted' state or wrong period
**Solution:** 
- Confirm all invoices are posted
- Check date filter matches invoice dates
- Verify company matches current user company

### Issue 2: ATS Validation Errors
**Cause:** Missing partner data or document authorization
**Solution:**
- Use validation feature to identify problematic records
- Click on error links to go directly to records
- Complete missing VAT, ID type, or authorization data

### Issue 3: Tax Groups Not Recognized
**Cause:** Tax group codes don't match expected values
**Solution:**
- Go to **Accounting → Configuration → Taxes**
- Edit tax groups to use correct codes:
  - `vat` for VAT >0%
  - `vat0` for VAT 0%
  - `novat` for No VAT
  - `ret_vat_b` for VAT withholding goods
  - `ret_vat_srv` for VAT withholding services
  - `ret_ir` for income tax withholding

### Issue 4: Wrong Tax Amounts
**Cause:** Tax configuration or base amount calculation
**Solution:**
- Verify tax percentages match Ecuador rates (12% VAT)
- Check withholding percentages (30%, 70%, 100% for VAT)
- Ensure taxes are applied to correct accounts

## Performance Tips

1. **Large Datasets:** Use date filters to limit data processing
2. **Monthly Processing:** Run ATS reports monthly, not yearly
3. **Validation First:** Always run validation before generating XML
4. **Archive Old Data:** Archive old fiscal year data to improve performance

## Troubleshooting Log

Enable debug mode to see detailed error messages:
1. Add `?debug=1` to URL
2. Check server logs for Python errors
3. Use browser developer tools for JavaScript errors

## Support Information

**Module Version:** 1.0.0
**Odoo Version:** 17.0 Community
**Ecuador Localization:** Required
**Last Updated:** 2024

For technical support, check:
1. Module logs in Odoo
2. Server error logs
3. Database constraint errors
4. Tax group configuration issues