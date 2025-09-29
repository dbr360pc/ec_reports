@echo off
echo.
echo ============================================
echo   Ecuador Reports - XML Validation & Upgrade
echo ============================================
echo.

echo STEP 1: Validating XML Files...
echo.

echo Checking VAT module menu XML...
python -c "import xml.etree.ElementTree as ET; ET.parse('l10n_ec_reports_vat/views/ec_reports_menu.xml'); print('✓ VAT menu XML is valid')" 2>nul || echo "✗ VAT menu XML has errors"

echo Checking ATS module menu XML...
python -c "import xml.etree.ElementTree as ET; ET.parse('l10n_ec_reports_ats_sri/views/menu_views.xml'); print('✓ ATS menu XML is valid')" 2>nul || echo "✗ ATS menu XML has errors"

echo Checking Form 103 module menu XML...
python -c "import xml.etree.ElementTree as ET; ET.parse('l10n_ec_reports_103/views/menu_views.xml'); print('✓ Form 103 menu XML is valid')" 2>nul || echo "✗ Form 103 menu XML has errors"

echo.
echo STEP 2: Module Structure Summary
echo.
echo Expected Menu Structure after upgrade:
echo.
echo   Accounting
echo   ├── Reports
echo   │   └── Ecuador Reports  ← Root menu from VAT module
echo   │       ├── VAT Reports (Forms 103/104)
echo   │       ├── ATS SRI Reports  ← Added by ATS module
echo   │       └── Form 103 (Withholdings)  ← Added by Form 103 module
echo   └── Configuration
echo       └── Ecuador Configuration  ← From VAT module
echo           ├── Form 104 Line Mappings
echo           └── ATS Catalogs  ← Added by ATS module
echo               ├── ID Types
echo               ├── Document Types
echo               ├── Payment Methods
echo               └── Sustain Codes
echo.

echo STEP 3: Upgrade Instructions
echo.
echo 1. RESTART ODOO SERVICE first
echo 2. Login to Odoo as Administrator
echo 3. Go to Apps menu
echo 4. Remove "Apps" filter (click X)
echo 5. Search for "Ecuador"
echo 6. Upgrade modules IN ORDER:
echo    a) Ecuador VAT Reports (base module)
echo    b) Ecuador ATS SRI Reports
echo    c) Ecuador Form 103 Reports
echo.
echo 7. If you get errors:
echo    - Check the Odoo server log for details
echo    - Verify all XML files are valid
echo    - Ensure proper module dependencies
echo.
echo 8. After successful upgrade:
echo    - Navigate to Accounting ^> Reports
echo    - Look for "Ecuador Reports" menu
echo    - Test each report wizard
echo.

echo STEP 4: Troubleshooting Common Issues
echo.
echo Problem: "Element odoo has extra content" error
echo Solution: Check XML indentation and ^<data^> wrapper
echo.
echo Problem: "External ID not found" error  
echo Solution: Install modules in correct order (VAT first)
echo.
echo Problem: Menus not visible
echo Solution: Check user permissions and clear browser cache
echo.

echo ============================================
echo   Ready to upgrade! Follow steps above.
echo ============================================
echo.
pause