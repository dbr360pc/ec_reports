@echo off
echo.
echo ================================================
echo   MINIMAL TEST - Single Menu Item
echo ================================================
echo.
echo TEST STRATEGY:
echo - Created minimal test_menu.xml with single menuitem
echo - Temporarily updated manifest to use test_menu.xml only
echo - Removed all complex attributes and structure
echo.
echo MINIMAL TEST FILE CONTENT:
echo ^<?xml version="1.0" encoding="utf-8"?^>
echo ^<odoo^>
echo     ^<menuitem id="test_menu" name="Test Menu" parent="account.menu_finance_reports"/^>
echo ^</odoo^>
echo.
echo IF THIS WORKS:
echo - The basic XML structure is correct
echo - The issue is with our complex menu structure
echo - We can gradually add complexity back
echo.
echo IF THIS FAILS:
echo - There's a fundamental issue with XML parsing
echo - Could be encoding, file path, or Odoo setup issue  
echo - Need to investigate deeper
echo.
echo ================================================
echo   NEXT: Try upgrading VAT module now
echo ================================================
echo.
echo 1. Restart Odoo service
echo 2. Upgrade VAT module only
echo 3. Check for "Test Menu" under Accounting ^> Reports
echo 4. Report back the result
echo.
pause