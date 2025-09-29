# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import UserError


class VatReportWizard(models.TransientModel):
    _name = 'vat.report.wizard'
    _description = 'VAT Report Wizard for Forms 103/104'

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
    
    # Results
    summary_data = fields.Text('Summary Data', readonly=True)
    detail_data = fields.Text('Detail Data', readonly=True)
    
    # Export files
    csv_summary_file = fields.Binary('CSV Summary File')
    csv_summary_filename = fields.Char('CSV Summary Filename')
    csv_detail_file = fields.Binary('CSV Detail File')
    csv_detail_filename = fields.Char('CSV Detail Filename')

    def action_generate_report(self):
        """Generate the VAT report data"""
        self.ensure_one()
        
        # Get date range
        date_from = datetime(self.year, int(self.month), 1).date()
        date_to = (date_from + relativedelta(months=1)) - relativedelta(days=1)
        
        # Get posted moves in the period
        moves = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ])
        
        summary_data, detail_data = self._compute_vat_data(moves)
        
        self.summary_data = str(summary_data)
        self.detail_data = str(detail_data)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vat.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_results': True}
        }

    def _compute_vat_data(self, moves):
        """Compute VAT data from moves using account.move.line tax information"""
        summary_data = []
        detail_data = []
        
        # Get 104 line mappings
        mappings = self.env['ec.104.line'].search([('active', '=', True)])
        mapping_dict = {}
        
        for mapping in mappings:
            mapping_dict[mapping.code] = {
                'name': mapping.name,
                'taxes': mapping.tax_ids.ids,
                'tags': mapping.tax_tag_ids.ids,
                'report_type': mapping.report_type,
                'section': mapping.section,
                'base_amount': 0.0,
                'tax_amount': 0.0,
                'details': []
            }
        
        # Process move lines similar to v9 approach but for v17
        for move in moves:
            # Get tax lines from the move
            tax_lines = move.line_ids.filtered(lambda l: l.tax_line_id)
            base_lines = move.line_ids.filtered(lambda l: l.tax_base_amount)
            
            # Process tax lines (actual tax amounts)
            for line in tax_lines:
                if not line.tax_line_id:
                    continue
                    
                tax_group_code = line.tax_line_id.tax_group_id.name if line.tax_line_id.tax_group_id else ''
                tax_code = line.tax_line_id.name
                
                # Map tax groups to 104 boxes based on v9 logic
                target_codes = self._get_target_codes_for_tax(line.tax_line_id, move.move_type, tax_group_code)
                
                for code in target_codes:
                    if code in mapping_dict:
                        mapping = mapping_dict[code]
                        if mapping['report_type'] in ['tax', 'both']:
                            mapping['tax_amount'] += abs(line.balance)
                            
                        # Add detail
                        detail = {
                            'invoice': move.name,
                            'partner': move.partner_id.name if move.partner_id else '',
                            'date': move.date.strftime('%Y-%m-%d'),
                            'base_amount': 0.0,
                            'tax_amount': abs(line.balance),
                            'document_type': move.move_type,
                            'tax_name': tax_code,
                        }
                        mapping['details'].append(detail)
            
            # Process base amounts
            for line in base_lines:
                if not line.tax_base_amount:
                    continue
                    
                # Get related taxes from tax_tag_ids or tax_ids
                related_taxes = []
                if line.tax_tag_ids:
                    # Find taxes that use these tags
                    related_taxes = self.env['account.tax'].search([
                        ('invoice_repartition_line_ids.tag_ids', 'in', line.tax_tag_ids.ids)
                    ])
                
                if not related_taxes and line.tax_ids:
                    related_taxes = line.tax_ids
                
                for tax in related_taxes:
                    tax_group_code = tax.tax_group_id.name if tax.tax_group_id else ''
                    target_codes = self._get_target_codes_for_tax(tax, move.move_type, tax_group_code)
                    
                    for code in target_codes:
                        if code in mapping_dict:
                            mapping = mapping_dict[code]
                            if mapping['report_type'] in ['base', 'both']:
                                mapping['base_amount'] += abs(line.tax_base_amount)
        
        # Build summary
        for code, mapping in mapping_dict.items():
            if mapping['base_amount'] or mapping['tax_amount']:
                summary_data.append({
                    'code': code,
                    'name': mapping['name'],
                    'section': mapping['section'],
                    'base_amount': mapping['base_amount'],
                    'tax_amount': mapping['tax_amount'],
                    'total_amount': mapping['base_amount'] + mapping['tax_amount']
                })
                
                detail_data.extend(mapping['details'])
        
        return summary_data, detail_data

    def _get_target_codes_for_tax(self, tax, move_type, tax_group_code):
        """Map tax to 103/104 box codes based on tax group and move type"""
        codes = []
        
        # Map based on tax group codes from v9 (adapted for v17)
        if 'vat' in tax_group_code.lower() or tax.amount > 0:  # VAT taxes
            if move_type in ['out_invoice', 'out_refund']:
                codes.append('521')  # Sales VAT (base)
                codes.append('799')  # VAT collected (tax amount)
            elif move_type in ['in_invoice', 'in_refund']:
                codes.append('611')  # Purchase VAT
                codes.append('741')  # VAT paid (credit)
        elif 'vat0' in tax_group_code.lower() or tax.amount == 0:  # 0% VAT
            if move_type in ['out_invoice', 'out_refund']:
                codes.append('522')  # Sales 0%
            elif move_type in ['in_invoice', 'in_refund']:
                codes.append('612')  # Purchase 0%
        elif 'novat' in tax_group_code.lower():  # No VAT
            if move_type in ['out_invoice', 'out_refund']:
                codes.append('523')  # Sales no VAT
            elif move_type in ['in_invoice', 'in_refund']:
                codes.append('613')  # Purchase no VAT
        elif 'ret_vat_b' in tax_group_code.lower():  # VAT retention goods
            codes.append('721')  # Retention VAT goods
        elif 'ret_vat_srv' in tax_group_code.lower():  # VAT retention services  
            codes.append('723')  # Retention VAT services
        elif 'ret_ir' in tax_group_code.lower():  # Income tax retention
            codes.append('731')  # Retention income tax
        elif 'comp' in tax_group_code.lower():  # Tax compensations
            codes.append('751')  # Compensations
            
        return codes

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
        self.csv_summary_filename = f'VAT_Summary_{self.year}_{self.month}.csv'
        
        # Generate detail CSV
        detail_csv = self._generate_detail_csv(detail_data)
        self.csv_detail_file = base64.b64encode(detail_csv.encode('utf-8'))
        self.csv_detail_filename = f'VAT_Detail_{self.year}_{self.month}.csv'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vat.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _generate_summary_csv(self, data):
        """Generate summary CSV content"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Box Code', 'Description', 'Section', 'Base Amount', 'Tax Amount', 'Total Amount'])
        
        # Data
        for row in data:
            writer.writerow([
                row['code'],
                row['name'],
                row['section'],
                f"{row['base_amount']:.2f}",
                f"{row['tax_amount']:.2f}",
                f"{row['total_amount']:.2f}"
            ])
        
        return output.getvalue()

    def _generate_detail_csv(self, data):
        """Generate detail CSV content"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Invoice', 'Partner', 'Date', 'Document Type', 'Base Amount', 'Tax Amount'])
        
        # Data
        for row in data:
            writer.writerow([
                row['invoice'],
                row['partner'],
                row['date'],
                row['document_type'],
                f"{row['base_amount']:.2f}",
                f"{row['tax_amount']:.2f}"
            ])
        
        return output.getvalue()

    def action_export_csv(self):
        """Export CSV files"""
        self.ensure_one()
        
        if not self.summary_data:
            raise UserError("No data to export. Please generate the report first.")
        
        # Generate CSV files
        summary_data = self._parse_summary_data()
        detail_data = self._parse_detail_data()
        
        # Create CSV files
        summary_csv = self._generate_summary_csv(summary_data)
        detail_csv = self._generate_detail_csv(detail_data)
        
        # Create filenames
        month_name = dict(self._fields['month'].selection)[self.month]
        summary_filename = f"VAT_103_Summary_{month_name}_{self.year}.csv"
        detail_filename = f"VAT_104_Detail_{month_name}_{self.year}.csv"
        
        # Create attachments
        summary_attachment = self.env['ir.attachment'].create({
            'name': summary_filename,
            'datas': base64.b64encode(summary_csv.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv',
        })
        
        detail_attachment = self.env['ir.attachment'].create({
            'name': detail_filename,
            'datas': base64.b64encode(detail_csv.encode('utf-8')), 
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv',
        })
        
        # Return download action for summary file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{summary_attachment.id}?download=true',
            'target': 'self',
        }

    def action_print_report(self):
        """Print PDF report"""
        self.ensure_one()
        
        if not self.summary_data:
            raise UserError("No data to print. Please generate the report first.")
        
        return self.env.ref('l10n_ec_reports_vat.action_report_ec_vat_103_104').report_action(self)
    
    def _parse_summary_data(self):
        """Parse summary data for export"""
        # This should parse the summary_data field content
        # For now, return sample data structure
        return [
            {'tax_name': 'IVA 12%', 'base_amount': 1000.00, 'tax_amount': 120.00},
            {'tax_name': 'IVA 0%', 'base_amount': 500.00, 'tax_amount': 0.00},
        ]
    
    def _parse_detail_data(self):
        """Parse detail data for export"""
        # This should parse the detail_data field content  
        # For now, return sample data structure
        return [
            {
                'invoice': 'INV/2024/001',
                'partner': 'Customer 1',
                'date': '2024-01-15',
                'document_type': 'Invoice',
                'base_amount': 1000.00,
                'tax_amount': 120.00
            }
        ]