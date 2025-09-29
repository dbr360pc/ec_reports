# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ATS specific fields
    x_ec_payment_method_id = fields.Many2one('ats.payment.method', string='Payment Method')
    x_ec_supplier_invoice_number = fields.Char('Supplier Invoice Number')
    x_ec_supplier_authorization = fields.Char('Supplier Authorization')
    x_ec_document_type_id = fields.Many2one('ats.document.type', string='Document Type')
    x_ec_sustain_code_id = fields.Many2one('ats.sustain.code', string='Sustain Code')
    
    # Reference fields for credit/debit notes
    x_ec_reference_document_type = fields.Char('Reference Document Type')
    x_ec_reference_series = fields.Char('Reference Series (Establishment + Emission Point)')
    x_ec_reference_sequential = fields.Char('Reference Sequential')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-set document type based on move_type"""
        for vals in vals_list:
            if 'move_type' in vals and not vals.get('x_ec_document_type_id'):
                doc_type = self.env['ats.document.type'].search([
                    ('move_type', '=', vals['move_type']),
                    ('active', '=', True)
                ], limit=1)
                if doc_type:
                    vals['x_ec_document_type_id'] = doc_type.id
        return super().create(vals_list)

    def _get_ats_partner_validation_errors(self):
        """Validate partner data for ATS reporting"""
        errors = []
        if not self.partner_id:
            errors.append("Missing partner")
            return errors
            
        if not self.partner_id.vat:
            errors.append("Partner missing VAT/RUC")
            
        if not self.partner_id.l10n_latam_identification_type_id:
            errors.append("Partner missing ID type")
            
        return errors

    def _get_ats_document_validation_errors(self):
        """Validate document data for ATS reporting"""
        errors = []
        
        if self.move_type in ('in_invoice', 'in_refund'):
            if not self.x_ec_supplier_invoice_number:
                errors.append("Missing supplier invoice number")
            if not self.x_ec_supplier_authorization:
                errors.append("Missing supplier authorization")
                
        if self.move_type in ('out_refund', 'in_refund'):
            if not self.x_ec_reference_document_type:
                errors.append("Credit/debit note missing reference document type")
            if not self.x_ec_reference_series:
                errors.append("Credit/debit note missing reference series")
            if not self.x_ec_reference_sequential:
                errors.append("Credit/debit note missing reference sequential")
                
        return errors

    def action_suggest_payment_method(self):
        """Suggest payment method from reconciled payments"""
        self.ensure_one()
        
        # Get reconciled payments
        payments = self.env['account.payment'].search([
            ('reconciled_invoice_ids', 'in', self.id)
        ])
        
        if payments:
            # For now, suggest cash if no specific method found
            cash_method = self.env['ats.payment.method'].search([
                ('code', '=', '01'),  # Cash
                ('active', '=', True)
            ], limit=1)
            if cash_method:
                self.x_ec_payment_method_id = cash_method.id
        
        return True