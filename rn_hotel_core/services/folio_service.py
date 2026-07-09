# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError


class RnHotelFolioService(models.AbstractModel):
    _name = 'rn.hotel.folio.service'
    _description = 'Folio Billing Service'

    def add_charge(self, folio_id, description, unit_price, quantity=1.0, charge_type='other'):
        folio = self.env['rn.hotel.folio'].browse(folio_id)
        if not folio.exists() or folio.state != 'open':
            raise UserError('Folio is not open.')
        return self.env['rn.hotel.folio.line'].create({
            'folio_id': folio.id,
            'charge_type': charge_type,
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price,
        }).id

    def generate_invoice(self, folio_id):
        folio = self.env['rn.hotel.folio'].browse(folio_id)
        if not folio.exists():
            raise UserError('Folio not found.')
        guest = folio.guest_id
        partner = guest.partner_id or self.env['res.partner'].create({
            'name': guest.name,
            'phone': guest.mobile,
            'email': guest.email,
        })
        if not guest.partner_id:
            guest.partner_id = partner.id
        lines = []
        for line in folio.line_ids:
            lines.append((0, 0, {
                'name': line.description,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
                'product_id': line.product_id.id if line.product_id else False,
            }))
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': lines,
        })
        folio.write({'invoice_id': invoice.id, 'state': 'invoiced'})
        return invoice.id
