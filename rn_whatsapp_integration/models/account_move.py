# -*- coding: utf-8 -*-

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = ['account.move', 'whatsapp.mixin']

    can_send_whatsapp = fields.Boolean(
        string='Can Send via WhatsApp',
        compute='_compute_can_send_whatsapp',
        help='True if this is a posted customer invoice/refund and the partner has a phone number.',
    )

    @api.depends('move_type', 'state', 'partner_id', 'partner_id.phone')
    def _compute_can_send_whatsapp(self):
        for move in self:
            move.can_send_whatsapp = move._can_send_whatsapp()

    def _whatsapp_phone_from_partner(self, partner):
        """Get WhatsApp number from partner: mobile preferred (if field exists), then phone. Digits only."""
        if not partner:
            return None
        # Use mobile if the model has it (e.g. from phone_validation), else phone
        raw = (getattr(partner, 'mobile', None) or partner.phone or '').strip()
        if not raw:
            return None
        digits = re.sub(r'\D', '', raw)
        if len(digits) < 8:
            return None
        return digits

    def _whatsapp_message_for_invoice(self, include_pdf_link=True, include_lines=True):
        """Build pre-filled WhatsApp message for this invoice (ID, amount, items with quantity, PDF link)."""
        self.ensure_one()
        parts = [
            _('Hi,'),
            _('Invoice: %s') % self.name,
            _('Amount: %s') % self.currency_id.format(self.amount_total),
            _('Due date: %s') % self.invoice_date_due,
        ]
        if include_lines and self.invoice_line_ids:
            parts.append('')
            parts.append(_('Items:'))
            for line in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                # One line per product: name, qty, unit price, subtotal
                name = (line.name or line.product_id.display_name or '')[:50]
                if line.quantity and line.price_unit is not None:
                    parts.append('• %s x %s = %s' % (
                        name,
                        line.quantity,
                        self.currency_id.format(line.price_subtotal),
                    ))
                else:
                    parts.append('• %s: %s' % (name, self.currency_id.format(line.price_subtotal)))
        if include_pdf_link and self.state == 'posted':
            self._portal_ensure_token()
            base_url = self.get_base_url()
            pdf_url = '%s/my/invoices/%s?access_token=%s&report_type=pdf&download=true' % (
                base_url.rstrip('/'),
                self.id,
                self.access_token,
            )
            parts.append('')
            parts.append(_('Download PDF: %s') % pdf_url)
        return '\n'.join(parts)

    def action_send_whatsapp(self):
        """Open WhatsApp with customer number and pre-filled message (and optional PDF link)."""
        self.ensure_one()
        if self.move_type not in ('out_invoice', 'out_refund', 'out_receipt'):
            raise UserError(_('WhatsApp send is only for customer invoices and refunds.'))
        if self.state != 'posted':
            raise UserError(_('Only posted invoices can be sent via WhatsApp.'))
        partner = self.partner_id
        phone = self._whatsapp_phone_from_partner(partner)
        if not phone:
            raise UserError(
                _('No WhatsApp number for %s. Please set Mobile or Phone on the contact.')
                % partner.display_name
            )
        message = self._whatsapp_message_for_invoice(include_pdf_link=True)
        self._whatsapp_log_outbound(phone, message)
        return self._whatsapp_act_url(phone, message)

    def _can_send_whatsapp(self):
        """True if this move can be sent via WhatsApp (customer doc, posted, has phone)."""
        self.ensure_one()
        if self.move_type not in ('out_invoice', 'out_refund', 'out_receipt'):
            return False
        if self.state != 'posted':
            return False
        return bool(self._whatsapp_phone_from_partner(self.partner_id))
