# -*- coding: utf-8 -*-
{
    'name': 'Ecuador ATS SRI Reports',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ecuador ATS (Anexo Transaccional Simplificado) Report Generation',
    'description': """
    Ecuador ATS Reports Module
    ==========================
    
    This module provides ATS reporting functionality for Ecuador:
    - ATS XML report generation for SRI
    - Sales, purchases, and withholdings reporting
    - Partner validation (VAT, ID type requirements)
    - Credit/debit note document references
    - Payment method mapping and reporting
    - XML export in official ATS format
    
    Features:
    - Wizard-based report generation
    - Configurable catalogs (ID types, document types, payment methods)
    - Validation reports with smart links
    - ZIP export (ATmmYYYY.zip format)
    - XML structure compliant with SRI requirements
    """,
    'author': 'Custom Development',
    'website': 'https://www.odoo.com',
    'depends': ['account', 'l10n_ec'],
    'data': [
        'security/ir.model.access.csv',
        'data/ats_catalog_data.xml',
        'views/ats_catalog_views.xml',
        'views/account_move_views.xml',
        'views/ats_report_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}