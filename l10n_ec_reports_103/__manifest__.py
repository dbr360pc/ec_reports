# -*- coding: utf-8 -*-
{
    'name': 'Ecuador Form 103 Reports (Withholdings)',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Ecuador Form 103 Withholding Reports',
    'description': """
    Ecuador Form 103 Reports Module
    ===============================
    
    This module provides Form 103 withholding reporting functionality for Ecuador:
    - VAT withholdings (goods and services)
    - Income tax withholdings
    - Integration with l10n_ec_account_edi when available
    - Monthly withholding summaries
    - PDF and CSV export capabilities
    
    Features:
    - Wizard-based report generation for withholdings
    - Automatic detection of withholding taxes
    - Summary and detail reports
    - Integration with ATS reporting
    - Export to PDF and CSV formats
    """,
    'author': 'Custom Development',
    'website': 'https://www.odoo.com',
    'depends': [
        'base',
        'account',
        'l10n_ec',
        'l10n_ec_reports_vat',
        'l10n_ec_reports_vat',  # For shared functionality
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/withholding_report_wizard_views.xml',
        'views/menu_views.xml',
        'reports/withholding_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}