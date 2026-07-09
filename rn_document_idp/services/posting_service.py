# -*- coding: utf-8 -*-
"""Create Odoo ERP records from validated documents."""

from odoo import fields, models
from odoo.exceptions import UserError


class RnDocumentIdpPostingService(models.AbstractModel):
    _name = 'rn.document.idp.posting.service'
    _description = 'IDP Posting Service'

    def post_document(self, document):
        document.ensure_one()
        if document.document_type == 'vendor_invoice':
            move = self._create_vendor_bill(document)
            return {
                'move_id': move.id,
                'action': {
                    'type': 'ir.actions.act_window',
                    'name': 'Vendor Bill',
                    'res_model': 'account.move',
                    'view_mode': 'form',
                    'res_id': move.id,
                },
            }
        raise UserError('Posting is not yet enabled for this document type.')

    def _create_vendor_bill(self, document):
        if not document.partner_id:
            raise UserError('Match or set a vendor before creating a vendor bill.')
        line_vals = []
        for line in document.line_ids:
            line_vals.append((0, 0, {
                'name': line.description,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
            }))
        if not line_vals:
            line_vals = [(0, 0, {
                'name': document.document_number or document.name,
                'quantity': 1.0,
                'price_unit': document.amount_untaxed or document.amount_total,
            })]
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': document.partner_id.id,
            'ref': document.document_number,
            'invoice_date': document.document_date or fields.Date.today(),
            'invoice_date_due': document.due_date,
            'currency_id': document.currency_id.id,
            'company_id': document.company_id.id,
            'invoice_line_ids': line_vals,
        })
        document.message_post(body=f'Vendor bill {move.name} created from IDP document.')
        return move
