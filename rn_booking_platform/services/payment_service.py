# -*- coding: utf-8 -*-
"""Payment and invoice automation stubs."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnBookingPaymentService(models.AbstractModel):
    """Create invoices and track payment state for appointments."""

    _name = 'rn.booking.payment.service'
    _description = 'Booking Payment Service'

    def create_invoice(self, appointments):
        """Create a customer invoice for appointments without one."""
        Move = self.env['account.move']
        for appt in appointments:
            if appt.invoice_id:
                continue
            product = appt.service_id.product_id
            line_name = appt.service_id.name
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': appt.partner_id.id,
                'invoice_origin': appt.name,
                'company_id': appt.company_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': line_name,
                    'quantity': 1,
                    'price_unit': appt.amount_total or appt.service_id.list_price or 0.0,
                    'product_id': product.id if product else False,
                })],
            }
            invoice = Move.create(invoice_vals)
            appt.invoice_id = invoice.id
            _logger.info('Invoice %s created for %s', invoice.name, appt.name)
        return True
