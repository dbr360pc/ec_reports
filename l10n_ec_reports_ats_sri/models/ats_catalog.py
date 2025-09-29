# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AtsIdType(models.Model):
    _name = 'ats.id.type'
    _description = 'ATS ID Type Catalog'
    _order = 'code'

    name = fields.Char('Description', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
                ('active', '=', True)
            ])
            if existing:
                raise models.ValidationError(f'Code "{record.code}" already exists.')


class AtsDocumentType(models.Model):
    _name = 'ats.document.type'
    _description = 'ATS Document Type Catalog'
    _order = 'code'

    name = fields.Char('Description', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)
    move_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
    ], string='Journal Entry Type')

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
                ('active', '=', True)
            ])
            if existing:
                raise models.ValidationError(f'Code "{record.code}" already exists.')


class AtsPaymentMethod(models.Model):
    _name = 'ats.payment.method'
    _description = 'ATS Payment Method Catalog'
    _order = 'code'

    name = fields.Char('Description', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', default=True)

    @api.constrains('code')
    def _check_unique_code(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
                ('active', '=', True)
            ])
            if existing:
                raise models.ValidationError(f'Code "{record.code}" already exists.')