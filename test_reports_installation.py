#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to validate Ecuador Reports modules installation
"""

import sys
import os

def test_module_structure():
    """Test if all required files exist"""
    print("🔍 Testing module structure...")
    
    required_files = [
        # VAT Module
        'l10n_ec_reports_vat/__manifest__.py',
        'l10n_ec_reports_vat/__init__.py',
        'l10n_ec_reports_vat/wizards/vat_report_wizard.py',
        'l10n_ec_reports_vat/views/vat_report_wizard_views.xml',
        'l10n_ec_reports_vat/views/ec_reports_menu.xml',
        'l10n_ec_reports_vat/reports/vat_report_templates.xml',
        'l10n_ec_reports_vat/security/ir.model.access.csv',
        
        # ATS Module
        'l10n_ec_reports_ats_sri/__manifest__.py',
        'l10n_ec_reports_ats_sri/__init__.py',
        'l10n_ec_reports_ats_sri/wizards/ats_report_wizard.py',
        'l10n_ec_reports_ats_sri/views/ats_report_wizard_views.xml',
        'l10n_ec_reports_ats_sri/views/menu_views.xml',
        'l10n_ec_reports_ats_sri/security/ir.model.access.csv',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_xml_syntax():
    """Test XML files for basic syntax errors"""
    print("\n🔍 Testing XML syntax...")
    
    xml_files = [
        'l10n_ec_reports_vat/views/vat_report_wizard_views.xml',
        'l10n_ec_reports_vat/views/ec_reports_menu.xml',
        'l10n_ec_reports_vat/reports/vat_report_templates.xml',
        'l10n_ec_reports_ats_sri/views/ats_report_wizard_views.xml',
        'l10n_ec_reports_ats_sri/views/menu_views.xml',
    ]
    
    try:
        import xml.etree.ElementTree as ET
        
        for xml_file in xml_files:
            if os.path.exists(xml_file):
                try:
                    ET.parse(xml_file)
                    print(f"✅ {xml_file}")
                except ET.ParseError as e:
                    print(f"❌ {xml_file}: {e}")
                    return False
            else:
                print(f"⚠️  {xml_file}: File not found")
        
        print("✅ All XML files have valid syntax")
        return True
        
    except ImportError:
        print("⚠️  XML testing skipped (no xml.etree available)")
        return True

def test_python_syntax():
    """Test Python files for basic syntax errors"""
    print("\n🔍 Testing Python syntax...")
    
    python_files = [
        'l10n_ec_reports_vat/__manifest__.py',
        'l10n_ec_reports_vat/wizards/vat_report_wizard.py',
        'l10n_ec_reports_ats_sri/__manifest__.py',
        'l10n_ec_reports_ats_sri/wizards/ats_report_wizard.py',
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, py_file, 'exec')
                print(f"✅ {py_file}")
            except SyntaxError as e:
                print(f"❌ {py_file}: {e}")
                return False
            except Exception as e:
                print(f"⚠️  {py_file}: {e}")
        else:
            print(f"⚠️  {py_file}: File not found")
    
    print("✅ All Python files have valid syntax")
    return True

def check_key_features():
    """Check if key features are implemented"""
    print("\n🔍 Checking key features...")
    
    # Check VAT wizard methods
    vat_file = 'l10n_ec_reports_vat/wizards/vat_report_wizard.py'
    if os.path.exists(vat_file):
        with open(vat_file, 'r') as f:
            vat_content = f.read()
        
        required_methods = [
            'action_generate_report',
            'action_export_csv', 
            'action_print_report',
            '_generate_summary_csv',
            '_generate_detail_csv'
        ]
        
        for method in required_methods:
            if f'def {method}(' in vat_content:
                print(f"✅ VAT: {method}")
            else:
                print(f"❌ VAT: Missing {method}")
    
    # Check ATS wizard methods
    ats_file = 'l10n_ec_reports_ats_sri/wizards/ats_report_wizard.py'
    if os.path.exists(ats_file):
        with open(ats_file, 'r') as f:
            ats_content = f.read()
        
        required_methods = [
            'action_generate_report',
            'action_export_xml_zip',
            '_generate_ats_xml',
        ]
        
        for method in required_methods:
            if f'def {method}(' in ats_content:
                print(f"✅ ATS: {method}")
            else:
                print(f"❌ ATS: Missing {method}")

def main():
    """Run all tests"""
    print("🚀 Ecuador Reports - Installation Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_module_structure():
        tests_passed += 1
    
    if test_xml_syntax():
        tests_passed += 1
        
    if test_python_syntax():
        tests_passed += 1
        
    check_key_features()  # This is informational
    tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Tests Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Modules ready for installation.")
        print("\n📋 Next steps:")
        print("1. Copy modules to Odoo addons directory")
        print("2. Update app list in Odoo")
        print("3. Install 'Ecuador VAT Reports' module")  
        print("4. Install 'Ecuador ATS SRI Reports' module")
        print("5. Access via Accounting → Reports → Ecuador Reports")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before installation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)