@echo off
echo.
echo ======================================
echo   XML Validation Test
echo ======================================
echo.

echo Testing VAT module menu XML...
python -c "
try:
    import xml.etree.ElementTree as ET
    ET.parse('l10n_ec_reports_vat/views/ec_reports_menu.xml')
    print('✓ VAT menu XML is valid')
except Exception as e:
    print('✗ VAT menu XML error:', str(e))
"

echo.
echo Testing ATS module menu XML...
python -c "
try:
    import xml.etree.ElementTree as ET
    ET.parse('l10n_ec_reports_ats_sri/views/menu_views.xml')
    print('✓ ATS menu XML is valid')
except Exception as e:
    print('✗ ATS menu XML error:', str(e))
"

echo.
echo Testing Form 103 module menu XML...
python -c "
try:
    import xml.etree.ElementTree as ET
    ET.parse('l10n_ec_reports_103/views/menu_views.xml')
    print('✓ Form 103 menu XML is valid')
except Exception as e:
    print('✗ Form 103 menu XML error:', str(e))
"

echo.
echo ======================================
echo   XML Validation Complete
echo ======================================
echo.
echo If all files show as valid, you can proceed with:
echo 1. Restart Odoo service
echo 2. Upgrade modules in Apps menu
echo.
pause