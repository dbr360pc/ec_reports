# -*- coding: utf-8 -*-
{
    'name': 'Ecuador VAT Reports (Form 103/104)',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ecuador VAT Report Generation for Forms 103 and 104',
    'description': """
    Ecuador VAT Reports Module
    ==========================
    
    This module provides VAT reporting functionality for Ecuador:
    - Form 103/104 VAT report generation
    - Configurable tax mapping to 104 boxes
    - Summary and detail reports
    - PDF and CSV export capabilities
    - Monthly reporting for posted entries only
    
    Features:
    - Wizard-based report generation
    - Configurable 104 line mappings
    - Summary view (base + VAT per line)
    - Detail view by invoice
    - Export to PDF (QWeb) and CSV
    """,
    'author': 'Custom Development',
    'website': 'https://www.odoo.com',
    'depends': ['account', 'l10n_ec'],
    'data': [
        'security/ir.model.access.csv',
        'data/ec_104_line_data.xml',
        'views/ec_104_line_views.xml',
        'views/test_menu.xml',
        'views/vat_report_wizard_views.xml',
        'reports/ec_vat_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}