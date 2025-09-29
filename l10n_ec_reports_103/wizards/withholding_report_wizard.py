# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import UserError


class WithholdingReportWizard(models.TransientModel):
    _name = 'withholding.report.wizard'
    _description = 'Withholding Report Wizard for Form 103'

    company_id = fields.Many2one('res.company', string='Company', 
                                required=True, 
                                default=lambda self: self.env.company)
    month = fields.Selection([
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December')
    ], string='Month', required=True, default=lambda self: str(date.today().month).zfill(2))
    
    year = fields.Integer('Year', required=True, default=lambda self: date.today().year)
    
    # Report type selection
    include_vat_withholdings = fields.Boolean('Include VAT Withholdings', default=True)
    include_income_withholdings = fields.Boolean('Include Income Tax Withholdings', default=True)
    
    # Results
    summary_data = fields.Text('Summary Data', readonly=True)
    detail_data = fields.Text('Detail Data', readonly=True)
    
    # Export files
    csv_summary_file = fields.Binary('CSV Summary File')
    csv_summary_filename = fields.Char('CSV Summary Filename')
    csv_detail_file = fields.Binary('CSV Detail File')
    csv_detail_filename = fields.Char('CSV Detail Filename')

    def action_generate_report(self):
        """Generate the withholding report data"""
        self.ensure_one()
        
        if not any([self.include_vat_withholdings, self.include_income_withholdings]):
            raise UserError("Please select at least one withholding type.")
        
        # Get date range
        date_from = datetime(self.year, int(self.month), 1).date()
        date_to = (date_from + relativedelta(months=1)) - relativedelta(days=1)
        
        summary_data, detail_data = self._compute_withholding_data(date_from, date_to)
        
        self.summary_data = str(summary_data)
        self.detail_data = str(detail_data)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'withholding.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_results': True}
        }

    def _compute_withholding_data(self, date_from, date_to):
        """Compute withholding data from moves"""
        summary_data = []
        detail_data = []
        
        # Get posted moves in the period
        moves = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ])
        
        # Process withholding tax lines
        withholding_summary = {}
        
        for move in moves:
            for line in move.line_ids.filtered(lambda l: l.tax_line_id):
                if not line.tax_line_id.tax_group_id:
                    continue
                    
                group_code = line.tax_line_id.tax_group_id.name.lower()
                tax_name = line.tax_line_id.name
                
                # Check if it's a withholding tax
                is_vat_withholding = any(code in group_code for code in ['ret_vat_b', 'ret_vat_srv'])
                is_income_withholding = 'ret_ir' in group_code
                
                if not ((is_vat_withholding and self.include_vat_withholdings) or 
                       (is_income_withholding and self.include_income_withholdings)):
                    continue
                
                # Categorize withholding
                if is_vat_withholding:
                    category = 'VAT Withholding - Goods' if 'ret_vat_b' in group_code else 'VAT Withholding - Services'
                    form_code = '721' if 'ret_vat_b' in group_code else '723'
                else:
                    category = 'Income Tax Withholding'
                    form_code = '731'
                
                # Aggregate by category and tax
                key = f"{category}_{tax_name}"
                if key not in withholding_summary:
                    withholding_summary[key] = {
                        'category': category,
                        'tax_name': tax_name,
                        'form_code': form_code,
                        'base_amount': 0.0,
                        'withholding_amount': 0.0,
                        'count': 0,
                        'details': []
                    }
                
                # Get base amount from related move lines
                base_amount = 0.0
                for base_line in move.line_ids.filtered(lambda l: l.tax_base_amount and line.tax_line_id.id in l.tax_ids.ids):
                    base_amount += abs(base_line.tax_base_amount)
                
                withholding_summary[key]['base_amount'] += base_amount
                withholding_summary[key]['withholding_amount'] += abs(line.balance)
                withholding_summary[key]['count'] += 1
                
                # Add detail
                detail = {
                    'invoice': move.name,
                    'partner': move.partner_id.name if move.partner_id else '',
                    'date': move.date.strftime('%Y-%m-%d'),
                    'document_type': move.move_type,
                    'base_amount': base_amount,
                    'withholding_amount': abs(line.balance),
                    'tax_name': tax_name,
                    'percentage': line.tax_line_id.amount,
                }
                withholding_summary[key]['details'].append(detail)
        
        # Build summary data
        for key, data in withholding_summary.items():
            summary_data.append({
                'form_code': data['form_code'],
                'category': data['category'],
                'tax_name': data['tax_name'],
                'base_amount': data['base_amount'],
                'withholding_amount': data['withholding_amount'],
                'count': data['count'],
                'average_rate': (data['withholding_amount'] / data['base_amount'] * 100) if data['base_amount'] else 0
            })
            
            detail_data.extend(data['details'])
        
        # Sort summary by form code and category
        summary_data.sort(key=lambda x: (x['form_code'], x['category']))
        
        return summary_data, detail_data

    def action_export_csv(self):
        """Export summary and detail to CSV"""
        self.ensure_one()
        
        if not self.summary_data:
            raise UserError("No data to export. Please generate the report first.")
        
        # Parse data
        summary_data = eval(self.summary_data)
        detail_data = eval(self.detail_data)
        
        # Generate summary CSV
        summary_csv = self._generate_summary_csv(summary_data)
        self.csv_summary_file = base64.b64encode(summary_csv.encode('utf-8'))
        self.csv_summary_filename = f'Withholdings_Summary_{self.year}_{self.month}.csv'
        
        # Generate detail CSV
        detail_csv = self._generate_detail_csv(detail_data)
        self.csv_detail_file = base64.b64encode(detail_csv.encode('utf-8'))
        self.csv_detail_filename = f'Withholdings_Detail_{self.year}_{self.month}.csv'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'withholding.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _generate_summary_csv(self, data):
        """Generate summary CSV content"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Form Code', 'Category', 'Tax Name', 'Base Amount', 
            'Withholding Amount', 'Count', 'Average Rate %'
        ])
        
        # Data
        for row in data:
            writer.writerow([
                row['form_code'],
                row['category'],
                row['tax_name'],
                f"{row['base_amount']:.2f}",
                f"{row['withholding_amount']:.2f}",
                row['count'],
                f"{row['average_rate']:.2f}"
            ])
        
        return output.getvalue()

    def _generate_detail_csv(self, data):
        """Generate detail CSV content"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Invoice', 'Partner', 'Date', 'Document Type', 'Tax Name', 
            'Percentage', 'Base Amount', 'Withholding Amount'
        ])
        
        # Data
        for row in data:
            writer.writerow([
                row['invoice'],
                row['partner'],
                row['date'],
                row['document_type'],
                row['tax_name'],
                f"{row['percentage']:.2f}",
                f"{row['base_amount']:.2f}",
                f"{row['withholding_amount']:.2f}"
            ])
        
        return output.getvalue()

    def action_print_report(self):
        """Print PDF report"""
        self.ensure_one()
        
        if not self.summary_data:
            raise UserError("No data to print. Please generate the report first.")
        
        return self.env.ref('l10n_ec_reports_103.action_report_withholding_103').report_action(self)