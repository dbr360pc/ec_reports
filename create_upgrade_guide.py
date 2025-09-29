#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ecuador Reports Module Update/Upgrade Script

This script helps with updating the Ecuador Reports modules after fixes.
"""

import sys
import os

def create_upgrade_guide():
    """Create upgrade guide"""
    
    upgrade_steps = """
🔧 Ecuador Reports - Module Upgrade Guide
=========================================

## ❌ Error Fixed:
"Nombre de modelo 'withholding.report.wizard' no valido en la definición de la acción"

## ✅ What Was Fixed:
1. Removed invalid model references from VAT module menu
2. Each module now properly defines only its own menus
3. Added proper module dependencies
4. Removed duplicate report definitions

## 📋 Upgrade Steps:

### Method 1: Module Upgrade (Recommended)
1. Go to Apps in Odoo
2. Remove any filters 
3. Search for "Ecuador"
4. Click "Upgrade" on each Ecuador module:
   - Ecuador VAT Reports (Form 103/104)
   - Ecuador ATS SRI Reports  
   - Ecuador Form 103 Withholdings

### Method 2: Restart & Update (If Method 1 fails)
1. Stop Odoo service:
   ```bash
   sudo systemctl stop odoo
   ```

2. Update module files in addons directory

3. Start Odoo with update:
   ```bash
   sudo -u odoo /usr/bin/odoo --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons --database=your_db_name --update=l10n_ec_reports_vat,l10n_ec_reports_ats_sri,l10n_ec_reports_103 --stop-after-init
   ```

4. Restart normally:
   ```bash
   sudo systemctl start odoo
   ```

### Method 3: Database Update (Advanced)
If you have database access:
```sql
-- Clean up any orphaned menu items
DELETE FROM ir_ui_menu WHERE action LIKE '%withholding.report.wizard%';
-- Then upgrade modules via interface
```

## ✅ Expected Result:
After upgrade, you should see in Accounting → Reports:
```
Ecuador Reports/
├── VAT Reports (103/104)     ← VAT module
├── ATS SRI Reports           ← ATS module  
└── Form 103 (Withholdings)   ← 103 module (if installed)
```

## 🚨 Installation Order:
1. Install: Ecuador VAT Reports (base module with menu structure)
2. Install: Ecuador ATS SRI Reports (depends on VAT module)  
3. Install: Ecuador Form 103 Withholdings (optional, depends on VAT module)

## 📞 Troubleshooting:
- If menus don't appear: Check module dependencies are satisfied
- If upgrade fails: Try Method 2 (restart with update)
- If database issues: Use Method 3 or contact support

## ✅ Files Modified:
- l10n_ec_reports_vat/views/ec_reports_menu.xml (removed invalid references)
- l10n_ec_reports_vat/__manifest__.py (cleaned up data files)
- l10n_ec_reports_ats_sri/__manifest__.py (added VAT dependency)
- l10n_ec_reports_103/__manifest__.py (added VAT dependency)
"""
    
    return upgrade_steps

def main():
    print("🔧 Creating upgrade guide...")
    
    guide = create_upgrade_guide()
    
    # Write to file
    with open('UPGRADE_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Upgrade guide created: UPGRADE_GUIDE.md")
    print("\n" + "="*50)
    print(guide)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)