# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Ec104Line(models.Model):
    _name = 'ec.104.line'
    _description = 'Ecuador 104 Form Line Mapping'
    _order = 'sequence, code'

    name = fields.Char('Description', required=True)
    code = fields.Char('Box Code', required=True, help="Form 104 box code")
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    report_type = fields.Selection([
        ('base', 'Tax Base'),
        ('tax', 'Tax Amount'),
        ('both', 'Both Base and Tax')
    ], string='Report Type', default='both', required=True)
    
    # Tax mapping
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    tax_tag_ids = fields.Many2many('account.account.tag', string='Tax Tags')
    
    # Form sections
    section = fields.Selection([
        ('sales', 'Sales'),
        ('purchases', 'Purchases'),
        ('other', 'Other')
    ], string='Section', default='sales', required=True)
    
    notes = fields.Text('Notes')

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
                ('active', '=', True)
            ])
            if existing:
                raise models.ValidationError(
                    f'Box code "{record.code}" already exists in another active mapping.'
                )