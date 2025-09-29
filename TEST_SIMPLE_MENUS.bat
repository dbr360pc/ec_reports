@echo off
echo.
echo ================================================
echo   Testing Simplified Menu Structure
echo ================================================
echo.
echo Changes made to isolate XML parsing issue:
echo - Added back ^<data^> wrappers
echo - Removed groups attributes temporarily  
echo - Removed web_icon attribute
echo - Simplified all menu items to basic structure
echo.
echo This should help identify if the issue is with:
echo - XML structure (data wrapper)
echo - Attribute syntax (groups, web_icon)
echo - Cross-module references
echo - Other XML validation issues
echo.
echo ================================================
echo   Ready to test upgrade
echo ================================================
echo.
echo 1. Try upgrading VAT module first (simplest structure)
echo 2. If it works, we can add back attributes gradually
echo 3. If it fails, the issue is with XML structure itself
echo.
echo After upgrade test:
echo - Check Accounting ^> Reports for "Ecuador Reports"
echo - Check if basic menu appears without errors
echo.
pause