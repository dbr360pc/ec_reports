@echo off
echo.
echo ============================================
echo   Ecuador Reports Module Upgrade Guide
echo ============================================
echo.
echo STEP 1: Restart Odoo Service
echo   - Stop and restart your Odoo service to reload module files
echo.
echo STEP 2: Login to Odoo as Administrator
echo   - Access your Odoo instance
echo   - Login with administrator credentials
echo.
echo STEP 3: Upgrade Modules
echo   - Go to Apps menu
echo   - Remove "Apps" filter (click X on the filter)
echo   - Search for "Ecuador"
echo   - Click "Upgrade" on each module:
echo     * Ecuador VAT Reports (Form 103/104)
echo     * Ecuador ATS SRI Reports  
echo     * Ecuador Form 103 Reports (Withholdings)
echo.
echo STEP 4: Verify Menu Structure
echo   - Go to Accounting menu
echo   - Look for "Reports" section
echo   - You should see "Ecuador Reports" with submenus:
echo     * VAT Reports (Forms 103/104)
echo     * ATS SRI Reports
echo     * Form 103 (Withholdings)
echo.
echo STEP 5: Check Configuration
echo   - Go to Accounting ^> Configuration
echo   - You should see "Ecuador Configuration" with:
echo     * Form 104 Line Mappings
echo     * ATS Catalogs (ID Types, Document Types, etc.)
echo.
echo STEP 6: Verify Technical Menu Items (Optional)
echo   - Go to Settings ^> Technical ^> Menu Items
echo   - Search for "menu_ec_reports_root"
echo   - Verify the menu structure exists
echo.
echo If menus don't appear:
echo   1. Clear browser cache and refresh
echo   2. Check user has Account User or Account Manager permissions
echo   3. Verify modules upgraded successfully without errors
echo.
pause