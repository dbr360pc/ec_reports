# Ecuador SRI Reports - User Documentation

## Overview

This package contains three custom Odoo 17 Community modules for Ecuador SRI (Servicio de Rentas Internas) reporting, migrated and enhanced from the original Odoo v9 Ecuador modules:

1. **l10n_ec_reports_vat** - VAT Reports (Form 104) - Enhanced with proper tax group mappings
2. **l10n_ec_reports_ats_sri** - ATS (Anexo Transaccional Simplificado) Reports - Complete XML generation
3. **l10n_ec_reports_103** - Form 103 (Withholdings) Reports - Dedicated withholding module

All modules are specifically designed for Ecuador localization, integrate with the `l10n_ec` module, and follow the migration strategy from the original v9 codebase while being rebuilt from scratch for Odoo 17 Community.

---

## Module 1: l10n_ec_reports_vat (VAT Reports Form 103/104)

### Purpose
Generate VAT reports for Ecuador's Form 103/104 with configurable tax mappings, summary and detail views, and multiple export formats.

### Dependencies
- `account` (Odoo accounting module)
- `l10n_ec` (Ecuador localization)

### Key Features

#### 1. VAT Report Wizard
**Location:** Accounting ▸ SRI Reports ▸ VAT Report (Form 103/104)

**Functionality:**
- Select company, month, and year for reporting
- Process only posted journal entries for the selected month
- Generate summary and detail reports
- Export to PDF and CSV formats

#### 2. 104 Form Line Mappings
**Location:** Accounting ▸ SRI Configuration ▸ 104 Form Line Mappings

**Purpose:**
Configure how taxes and tax tags map to specific boxes on Form 104.

**Fields:**
- **Box Code:** Form 104 box identifier
- **Description:** Human-readable description
- **Section:** Sales, Purchases, or Other
- **Report Type:** Base, Tax, or Both
- **Taxes:** Link specific taxes to this box
- **Tax Tags:** Link tax tags to this box

#### 3. Enhanced Tax Mappings (Based on v9 Analysis)
The module includes comprehensive mappings for both Forms 103 and 104:

**Form 103 (Withholdings):**
- **721:** VAT Withholdings on Goods
- **723:** VAT Withholdings on Services  
- **731:** Income Tax Withholdings

**Form 104 (VAT):**
- **521:** Sales with VAT (different from 0%)
- **522:** Sales at 0% VAT
- **523:** Sales not subject to VAT
- **611:** Purchases with VAT (different from 0%)
- **612:** Purchases at 0% VAT
- **613:** Purchases not subject to VAT
- **731:** VAT Collected (IVA Causado)
- **741:** VAT Paid (IVA Pagado)
- **751:** Tax Compensations

### Usage Instructions

#### Step 1: Configure Tax Mappings
1. Go to **Accounting ▸ SRI Configuration ▸ 104 Form Line Mappings**
2. Review and modify the default mappings
3. Map your company's taxes to the appropriate form boxes
4. Set the correct report type for each mapping

#### Step 2: Generate VAT Report
1. Go to **Accounting ▸ SRI Reports ▸ VAT Report (Form 103/104)**
2. Select company, month, and year
3. Click **Generate Report**
4. Review the summary and detail data
5. Use **Export CSV** for data files or **Print PDF** for formatted report

#### Step 3: Review Output
- **Summary:** Shows totals by form box with base amounts, tax amounts, and totals
- **Detail:** Lists individual invoices contributing to each box
- **CSV Files:** Separate files for summary and detail data
- **PDF Report:** Formatted report suitable for presentation

---

## Module 2: l10n_ec_reports_103 (Form 103 - Withholdings)

### Purpose
Generate Form 103 withholding reports for Ecuador, handling VAT and Income Tax withholdings with automatic tax group detection.

### Dependencies
- `account` (Odoo accounting module)
- `l10n_ec` (Ecuador localization)
- `l10n_ec_reports_vat` (for shared tax mappings)

### Key Features

#### 1. Withholding Report Wizard
**Location:** Accounting ▸ SRI Reports ▸ Form 103 (Withholdings)

**Functionality:**
- Select company, month, and year for reporting
- Choose withholding types: VAT withholdings, Income tax withholdings
- Process withholding tax lines from posted entries
- Generate summary by tax type and detail by transaction

#### 2. Automatic Tax Detection
**Withholding Types Detected:**
- **VAT Withholdings on Goods:** Tax group `ret_vat_b` → Form box 721
- **VAT Withholdings on Services:** Tax group `ret_vat_srv` → Form box 723
- **Income Tax Withholdings:** Tax group `ret_ir` → Form box 731

#### 3. Integration with l10n_ec_account_edi
**Future Enhancement:**
When `l10n_ec_account_edi` is installed, the module can fetch withholding records directly from electronic withholding documents.

### Usage Instructions

#### Step 1: Configure Withholding Taxes
1. Ensure your withholding taxes have proper tax groups:
   - VAT withholdings on goods: `ret_vat_b`
   - VAT withholdings on services: `ret_vat_srv`
   - Income tax withholdings: `ret_ir`

#### Step 2: Generate Form 103 Report
1. Go to **Accounting ▸ SRI Reports ▸ Form 103 (Withholdings)**
2. Select company, month, year
3. Choose withholding types to include
4. Click **Generate Report**
5. Review summary and detail data
6. Export to PDF or CSV as needed

#### Step 3: Review Output
- **Summary:** Shows totals by withholding category with average rates
- **Detail:** Lists individual transactions with base amounts and withholding amounts
- **Integration:** Data feeds into ATS reporting for complete SRI compliance

---

## Module 3: l10n_ec_reports_ats_sri (ATS Reports)

### Purpose
Generate ATS (Anexo Transaccional Simplificado) XML reports for SRI submission, including sales, purchases, and withholdings data.

### Dependencies
- `account` (Odoo accounting module)
- `l10n_ec` (Ecuador localization)
- `l10n_ec_account_edi` (optional, for withholdings)

### Key Features

#### 1. ATS Report Wizard
**Location:** Accounting ▸ SRI Reports ▸ ATS Report

**Functionality:**
- Select company, month, and year
- Choose report sections: Sales, Purchases, Withholdings
- Validate data before generating XML
- Export as ZIP file (ATmmYYYY.zip format)

#### 2. Partner and Document Validation
**Automatic validation checks:**
- Partner must have VAT/RUC and ID type
- Vendor bills must have invoice number and authorization
- Credit/debit notes must reference original documents
- Payment methods must be specified

#### 3. Extended Invoice Fields
**Additional fields on invoices:**
- **Payment Method:** ATS payment method catalog
- **Supplier Invoice Number:** For vendor bills
- **Supplier Authorization:** For vendor bills
- **Document Type:** ATS document type
- **Reference Info:** For credit/debit notes

#### 4. Enhanced Configurable Catalogs (Based on v9 Analysis)
**Location:** Accounting ▸ SRI Configuration ▸ ATS Catalogs

**Available catalogs:**
- **ID Types:** Separate codes for providers (01-03) and clients (04-07)
- **Document Types:** Complete SRI catalog with move_type mapping
- **Payment Methods:** Full SRI payment method catalog (01-20)
- **Sustain Codes:** Purchase justification codes for tax credit (01-05)

### Usage Instructions

#### Step 1: Configure Master Data
1. **Set up Company RUC:**
   - Ensure company has VAT/RUC configured
   
2. **Configure Partner Data:**
   - All partners must have VAT and ID type
   - Providers use codes 01-03, clients use codes 04-07
   - Use **Accounting ▸ SRI Configuration ▸ ATS Catalogs ▸ ID Types**

3. **Review Enhanced Catalogs:**
   - **Sustain Codes:** Set default sustain codes for purchase justification
   - **Document Types:** Verify mapping to Odoo move types
   - **Payment Methods:** Complete SRI catalog pre-loaded
   - Add custom entries if needed

#### Step 2: Complete Invoice Information
1. **For all invoices:**
   - Select appropriate payment method
   - Use "Suggest Payment Method" button when available
   
2. **For vendor bills:**
   - Select sustain code (purchase justification)
   - Enter supplier invoice number (format: ESTAB-EMISION-SEQUENTIAL)
   - Enter supplier authorization number
   
3. **For credit/debit notes:**
   - Complete reference document information
   - Include document type, series, and sequential
   - System auto-detects from reversed_entry_id when possible

#### Step 3: Generate ATS Report
1. Go to **Accounting ▸ SRI Reports ▸ ATS Report**
2. Select company, month, year
3. Choose report sections to include
4. Click **Generate ATS Report**
5. **If validation errors appear:**
   - Review the validation report
   - Click on invoice links to fix issues
   - Re-run the report after corrections
6. **If successful:**
   - Download the ZIP file
   - Submit to SRI portal

#### Step 4: Handle Validation Errors
**Common validation errors and solutions:**

| Error | Solution |
|-------|----------|
| Partner missing VAT | Add VAT/RUC to partner record |
| Partner missing ID type | Set identification type on partner |
| Missing supplier invoice number | Add to vendor bill |
| Missing supplier authorization | Add authorization to vendor bill |
| Missing payment method | Select from ATS payment method catalog |
| Credit note missing reference | Complete reference document fields |

---

## Technical Implementation Details

### VAT Module Architecture
```
l10n_ec_reports_vat/
├── models/
│   └── ec_104_line.py          # Tax mapping configuration
├── wizards/
│   └── vat_report_wizard.py    # Report generation logic
├── views/                       # UI definitions
├── reports/                     # PDF report templates
├── data/                        # Default mappings
└── security/                    # Access rights
```

### ATS Module Architecture
```
l10n_ec_reports_ats_sri/
├── models/
│   ├── ats_catalog.py          # Catalog models (ID types, doc types, payment methods)
│   └── account_move.py         # Invoice extensions
├── wizards/
│   └── ats_report_wizard.py    # ATS generation and validation
├── views/                       # UI definitions
├── data/                        # Default catalog data
└── security/                    # Access rights
```

### XML Structure (ATS)
The ATS XML follows the official SRI structure:
```xml
<iva>
    <TipoIDInformante>R</TipoIDInformante>
    <IdInformante>RUC</IdInformante>
    <!-- Header info -->
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
    <retenciones>
        <!-- Withholding details -->
    </retenciones>
</iva>
```

---

## Installation Instructions

### Prerequisites
1. Odoo 17 Community Edition
2. Ecuador localization module (`l10n_ec`) installed
3. Accounting module (`account`) configured

### Installation Steps
1. Copy both module folders to your Odoo addons directory
2. Restart Odoo server
3. Go to **Apps** menu
4. Remove "Apps" filter and search for "Ecuador"
5. Install both modules:
   - **Ecuador VAT Reports (Form 103/104)**
   - **Ecuador ATS Reports**

### Post-Installation Setup
1. Configure company VAT/RUC
2. Set up partner identification types
3. Review and customize tax mappings for VAT module
4. Configure ATS catalogs as needed

---

## Troubleshooting

### Common Issues

**Issue:** VAT report shows no data
**Solution:** 
- Verify tax mappings are configured
- Ensure moves are in "posted" state
- Check that taxes are properly applied to invoices

**Issue:** ATS validation fails
**Solution:**
- Review validation report carefully
- Fix partner data (VAT, ID type)
- Complete missing invoice information
- Ensure all required fields are filled

**Issue:** Export files are empty
**Solution:**
- Generate report first before exporting
- Check user permissions for the accounting group
- Verify data exists for the selected period

### Support and Customization

For technical support or customizations:
1. Check the validation reports for specific error messages
2. Review the module logs in Odoo's developer mode
3. Consult with an Odoo technical specialist for advanced modifications

The modules are designed to be maintainable and extensible. You can modify the tax mappings, add new catalog entries, or customize the XML output format as needed for your specific requirements.

---

## Compliance Notes

- Both modules generate reports according to Ecuador SRI requirements
- VAT calculations are based on Odoo's standard tax computation
- ATS XML format follows official SRI specifications
- All amounts are reported as positive values in ATS
- Date formats use dd/mm/yyyy as required by SRI
- Decimal amounts use dot notation in XML output

Regular updates may be needed to maintain compliance with changing SRI requirements.