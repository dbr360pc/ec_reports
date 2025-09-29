# -*- coding: utf-8 -*-
import base64
import zipfile
import io
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AtsReportWizard(models.TransientModel):
    _name = 'ats.report.wizard'
    _description = 'ATS Report Wizard'

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
    
    # Report options
    include_sales = fields.Boolean('Include Sales', default=True)
    include_purchases = fields.Boolean('Include Purchases', default=True)
    include_withholdings = fields.Boolean('Include Withholdings', default=False)
    
    # Results
    validation_report = fields.Html('Validation Report', readonly=True)
    xml_file = fields.Binary('ATS XML File')
    xml_filename = fields.Char('XML Filename')
    zip_file = fields.Binary('ATS ZIP File')
    zip_filename = fields.Char('ZIP Filename')

    def action_generate_report(self):
        """Generate ATS report"""
        self.ensure_one()
        
        # Validate inputs
        if not any([self.include_sales, self.include_purchases, self.include_withholdings]):
            raise UserError("Please select at least one report type.")
        
        # Get date range
        date_from = datetime(self.year, int(self.month), 1).date()
        date_to = (date_from + relativedelta(months=1)) - relativedelta(days=1)
        
        # Validate company RUC
        if not self.company_id.vat:
            raise UserError("Company must have a VAT/RUC configured.")
        
        # Generate validation report
        validation_errors = self._generate_validation_report(date_from, date_to)
        
        if validation_errors:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ats.report.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {'show_validation': True}
            }
        
        # Generate XML
        xml_content = self._generate_ats_xml(date_from, date_to)
        
        # Create files
        self._create_export_files(xml_content)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ats.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_results': True}
        }

    def _generate_validation_report(self, date_from, date_to):
        """Generate validation report"""
        errors = []
        
        # Get moves in period
        domain = [
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        
        if self.include_sales:
            sales_domain = domain + [('move_type', 'in', ['out_invoice', 'out_refund'])]
            sales_moves = self.env['account.move'].search(sales_domain)
            errors.extend(self._validate_moves(sales_moves, 'Sales'))
        
        if self.include_purchases:
            purchase_domain = domain + [('move_type', 'in', ['in_invoice', 'in_refund'])]
            purchase_moves = self.env['account.move'].search(purchase_domain)
            errors.extend(self._validate_moves(purchase_moves, 'Purchases'))
        
        if errors:
            self.validation_report = self._format_validation_report(errors)
            return errors
        else:
            self.validation_report = "<p><strong>✓ All validations passed successfully!</strong></p>"
            return []

    def _validate_moves(self, moves, section):
        """Validate moves for ATS requirements"""
        errors = []
        
        for move in moves:
            move_errors = []
            
            # Partner validation
            partner_errors = move._get_ats_partner_validation_errors()
            move_errors.extend(partner_errors)
            
            # Document validation
            doc_errors = move._get_ats_document_validation_errors()
            move_errors.extend(doc_errors)
            
            # Payment method validation
            if not move.x_ec_payment_method_id:
                move_errors.append("Missing payment method")
            
            if move_errors:
                errors.append({
                    'section': section,
                    'move_id': move.id,
                    'move_name': move.name,
                    'partner_name': move.partner_id.name if move.partner_id else 'Unknown',
                    'errors': move_errors
                })
        
        return errors

    def _format_validation_report(self, errors):
        """Format validation report as HTML"""
        html = "<h4>Validation Errors Found:</h4>"
        html += "<p>The following issues must be resolved before generating the ATS report:</p>"
        
        current_section = None
        for error in errors:
            if error['section'] != current_section:
                if current_section:
                    html += "</ul>"
                html += f"<h5>{error['section']}:</h5><ul>"
                current_section = error['section']
            
            html += f"<li><strong>{error['move_name']}</strong> - {error['partner_name']}<br/>"
            html += "<ul>"
            for err in error['errors']:
                html += f"<li>{err}</li>"
            html += "</ul></li>"
        
        if current_section:
            html += "</ul>"
        
        return html

    def _generate_ats_xml(self, date_from, date_to):
        """Generate ATS XML content"""
        # Root element
        root = Element('iva')
        
        # Header info
        ruc = self.company_id.vat.replace('-', '')
        period = f"{self.year}{self.month.zfill(2)}"
        
        # TipoIDInformante
        SubElement(root, 'TipoIDInformante').text = 'R'
        # IdInformante
        SubElement(root, 'IdInformante').text = ruc
        # razonSocial
        SubElement(root, 'razonSocial').text = self.company_id.name
        # Anio
        SubElement(root, 'Anio').text = str(self.year)
        # Mes
        SubElement(root, 'Mes').text = self.month.zfill(2)
        # numEstabRuc
        SubElement(root, 'numEstabRuc').text = '001'
        # totalVentas
        SubElement(root, 'totalVentas').text = '0.00'
        # codigoOperativo
        SubElement(root, 'codigoOperativo').text = 'IVA'
        
        # Sales section
        if self.include_sales:
            ventas = SubElement(root, 'ventas')
            self._add_sales_to_xml(ventas, date_from, date_to)
        
        # Purchases section
        if self.include_purchases:
            compras = SubElement(root, 'compras')
            self._add_purchases_to_xml(compras, date_from, date_to)
        
        # Withholdings section
        if self.include_withholdings:
            retenciones = SubElement(root, 'retenciones')
            self._add_withholdings_to_xml(retenciones, date_from, date_to)
        
        # Format XML
        rough_string = tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8')

    def _add_sales_to_xml(self, parent, date_from, date_to):
        """Add sales data to XML"""
        moves = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ])
        
        for move in moves:
            detalle_ventas = SubElement(parent, 'detalleVentas')
            
            # Basic info
            SubElement(detalle_ventas, 'tpIdCliente').text = move.partner_id.l10n_latam_identification_type_id.l10n_ec_code or '05'
            SubElement(detalle_ventas, 'idCliente').text = move.partner_id.vat or ''
            SubElement(detalle_ventas, 'parteRel').text = 'NO'
            SubElement(detalle_ventas, 'tipoCliente').text = '01'
            SubElement(detalle_ventas, 'denoCli').text = move.partner_id.name
            
            # Document info
            SubElement(detalle_ventas, 'tipoComprobante').text = move.x_ec_document_type_id.code or '18'
            SubElement(detalle_ventas, 'numeroComprobantes').text = '1'
            SubElement(detalle_ventas, 'baseNoGraIva').text = '0.00'
            SubElement(detalle_ventas, 'baseImponible').text = '0.00'
            SubElement(detalle_ventas, 'baseImpGrav').text = f"{abs(move.amount_untaxed):.2f}"
            SubElement(detalle_ventas, 'montoIva').text = f"{abs(move.amount_tax):.2f}"
            SubElement(detalle_ventas, 'valorRetIva').text = '0.00'
            SubElement(detalle_ventas, 'valorRetRenta').text = '0.00'
            
            # Payment info
            formas_pago = SubElement(detalle_ventas, 'formasDePago')
            forma_pago = SubElement(formas_pago, 'formaPago')
            SubElement(forma_pago, 'formaPago').text = move.x_ec_payment_method_id.code or '01'
            SubElement(forma_pago, 'total').text = f"{abs(move.amount_total):.2f}"

    def _add_purchases_to_xml(self, parent, date_from, date_to):
        """Add purchases data to XML based on v9 logic adapted for v17"""
        moves = self.env['account.move'].search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('move_type', 'in', ['in_invoice', 'in_refund'])
        ])
        
        for move in moves:
            # Skip if partner doesn't have passport as ID type (from v9 logic)
            if move.partner_id.l10n_latam_identification_type_id and \
               move.partner_id.l10n_latam_identification_type_id.name == 'pasaporte':
                continue
                
            detalle_compras = SubElement(parent, 'detalleCompras')
            
            # Calculate VAT breakdowns
            amount_vat, amount_vat0, amount_novat = self._get_vat_breakdown(move)
            ret_vat_goods, ret_vat_services = self._get_vat_retentions(move)
            
            # Basic info
            SubElement(detalle_compras, 'codSustento').text = move.x_ec_sustain_code_id.code if move.x_ec_sustain_code_id else '01'
            SubElement(detalle_compras, 'tpIdProv').text = self._get_partner_id_type_code(move.partner_id, 'provider')
            SubElement(detalle_compras, 'idProv').text = move.partner_id.vat or ''
            SubElement(detalle_compras, 'tipoComprobante').text = move.x_ec_document_type_id.code if move.x_ec_document_type_id else '01'
            SubElement(detalle_compras, 'parteRel').text = 'NO'
            SubElement(detalle_compras, 'fechaRegistro').text = move.date.strftime('%d/%m/%Y')
            
            # Document number breakdown (establishment-emission-sequential)
            inv_number = move.x_ec_supplier_invoice_number or move.ref or '001001001'
            if len(inv_number) >= 9:
                establecimiento = inv_number[:3]
                punto_emision = inv_number[3:6]
                secuencial = inv_number[6:15] if len(inv_number) > 6 else inv_number[6:]
            else:
                establecimiento = '001'
                punto_emision = '001'
                secuencial = inv_number
                
            SubElement(detalle_compras, 'establecimiento').text = establecimiento
            SubElement(detalle_compras, 'puntoEmision').text = punto_emision
            SubElement(detalle_compras, 'secuencial').text = secuencial
            SubElement(detalle_compras, 'fechaEmision').text = move.invoice_date.strftime('%d/%m/%Y') if move.invoice_date else move.date.strftime('%d/%m/%Y')
            SubElement(detalle_compras, 'autorizacion').text = move.x_ec_supplier_authorization or '1234567890'
            
            # Tax amounts
            SubElement(detalle_compras, 'baseNoGraIva').text = f'{amount_novat:.2f}'
            SubElement(detalle_compras, 'baseImponible').text = f'{amount_vat0:.2f}'
            SubElement(detalle_compras, 'baseImpGrav').text = f'{amount_vat:.2f}'
            SubElement(detalle_compras, 'baseImpExe').text = '0.00'
            SubElement(detalle_compras, 'montoIce').text = '0.00'
            SubElement(detalle_compras, 'montoIva').text = f'{abs(move.amount_tax):.2f}'
            
            # VAT retentions
            SubElement(detalle_compras, 'valorRetBienes').text = f'{ret_vat_goods:.2f}'
            SubElement(detalle_compras, 'valorRetServicios').text = f'{ret_vat_services:.2f}'
            SubElement(detalle_compras, 'valorRetIva').text = f'{(ret_vat_goods + ret_vat_services):.2f}'
            
            # Payment info
            formas_pago = SubElement(detalle_compras, 'formasDePago')
            forma_pago = SubElement(formas_pago, 'formaPago')
            SubElement(forma_pago, 'formaPago').text = move.x_ec_payment_method_id.code if move.x_ec_payment_method_id else '01'
            SubElement(forma_pago, 'total').text = f'{abs(move.amount_total):.2f}'
            
            # Credit/debit note references
            if move.move_type == 'in_refund' and move.reversed_entry_id:
                self._add_credit_note_reference(detalle_compras, move)

    def _add_withholdings_to_xml(self, parent, date_from, date_to):
        """Add withholdings data to XML"""
        # For now, just add empty structure
        # This would need integration with l10n_ec_account_edi for actual withholding records
        pass

    def _create_export_files(self, xml_content):
        """Create XML and ZIP export files"""
        # XML file
        ruc = self.company_id.vat.replace('-', '')
        period = f"{self.year}{self.month.zfill(2)}"
        
        xml_filename = f"ATS_{ruc}_{period}.xml"
        self.xml_file = base64.b64encode(xml_content)
        self.xml_filename = xml_filename
        
        # ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(xml_filename, xml_content)
        
        zip_filename = f"AT{self.month}{str(self.year)[2:]}.zip"
        self.zip_file = base64.b64encode(zip_buffer.getvalue())
        self.zip_filename = zip_filename

    def _get_vat_breakdown(self, move):
        """Get VAT breakdown: vat (>0%), vat0 (0%), novat (no VAT)"""
        amount_vat = 0.0
        amount_vat0 = 0.0
        amount_novat = 0.0
        
        for line in move.invoice_line_ids:
            if line.tax_ids:
                for tax in line.tax_ids:
                    if tax.amount > 0:
                        amount_vat += line.price_subtotal
                    elif tax.amount == 0:
                        amount_vat0 += line.price_subtotal
                    break  # Take first tax
            else:
                amount_novat += line.price_subtotal
                
        return amount_vat, amount_vat0, amount_novat

    def _get_vat_retentions(self, move):
        """Get VAT retentions for goods and services"""
        ret_goods = 0.0
        ret_services = 0.0
        
        # Look for retention tax lines
        for line in move.line_ids.filtered(lambda l: l.tax_line_id):
            if line.tax_line_id.tax_group_id:
                group_name = line.tax_line_id.tax_group_id.name.lower()
                if 'ret_vat_b' in group_name:  # VAT retention goods
                    ret_goods += abs(line.balance)
                elif 'ret_vat_srv' in group_name:  # VAT retention services
                    ret_services += abs(line.balance)
                    
        return ret_goods, ret_services

    def _get_partner_id_type_code(self, partner, partner_type='client'):
        """Get partner ID type code for ATS"""
        if not partner.l10n_latam_identification_type_id:
            return '05'  # Default to cedula
            
        id_type_name = partner.l10n_latam_identification_type_id.name.lower()
        
        # Map based on partner type (client vs provider)
        if partner_type == 'provider':
            if 'ruc' in id_type_name:
                return '01'
            elif 'cedula' in id_type_name:
                return '02'  
            elif 'pasaporte' in id_type_name:
                return '03'
        else:  # client
            if 'ruc' in id_type_name:
                return '04'
            elif 'cedula' in id_type_name:
                return '05'
            elif 'pasaporte' in id_type_name:
                return '06'
            elif 'consumidor' in id_type_name:
                return '07'
                
        return '05'  # Default

    def _add_credit_note_reference(self, detalle_compras, move):
        """Add credit/debit note reference information"""
        original_move = move.reversed_entry_id
        if original_move:
            # Use custom reference fields if available, otherwise derive from original
            doc_type = move.x_ec_reference_document_type or '01'  # Default to invoice
            series = move.x_ec_reference_series or '001001'
            sequential = move.x_ec_reference_sequential or original_move.name
            
            SubElement(detalle_compras, 'docModificado').text = doc_type
            SubElement(detalle_compras, 'estabModificado').text = series[:3]
            SubElement(detalle_compras, 'ptoEmiModificado').text = series[3:6] if len(series) > 3 else '001'
            SubElement(detalle_compras, 'secModificado').text = sequential
            SubElement(detalle_compras, 'autModificado').text = original_move.ref or '1234567890'

    def action_open_move(self):
        """Open account move from validation report"""
        move_id = self.env.context.get('move_id')
        if move_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': move_id,
                'view_mode': 'form',
                'target': 'current',
            }