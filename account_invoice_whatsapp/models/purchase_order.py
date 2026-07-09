# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'whatsapp.mixin']

    can_send_whatsapp = fields.Boolean(
        string='Can Send via WhatsApp',
        compute='_compute_can_send_whatsapp',
    )

    @api.depends('state', 'partner_id', 'partner_id.phone')
    def _compute_can_send_whatsapp(self):
        for order in self:
            order.can_send_whatsapp = order._can_send_whatsapp()

    def _whatsapp_message_for_purchase_order(self, include_pdf_link=True):
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        parts = [
            _('Hi,'),
            _('Purchase Order: %s') % self.name,
            _('Amount: %s') % currency.format(self.amount_total),
        ]
        if self.order_line:
            parts.append('')
            parts.append(_('Items:'))
            for line in self.order_line.filtered(lambda l: not l.display_type):
                name = (line.name or line.product_id.display_name or '')[:50]
                parts.append('• %s x %s = %s' % (
                    name,
                    line.product_qty,
                    currency.format(line.price_subtotal),
                ))
        if include_pdf_link and self.state == 'purchase':
            self._portal_ensure_token()
            base_url = self.get_base_url()
            pdf_url = base_url.rstrip('/') + self.get_portal_url(report_type='pdf', download=True)
            parts.append('')
            parts.append(_('View / Download: %s') % pdf_url)
        return '\n'.join(parts)

    def action_send_whatsapp(self):
        self.ensure_one()
        if self.state == 'cancel':
            raise UserError(_('Cannot send a cancelled order via WhatsApp.'))
        partner = self.partner_id
        phone = self._whatsapp_phone_from_partner(partner)
        if not phone:
            raise UserError(
                _('No WhatsApp number for %s. Please set Mobile or Phone on the contact.')
                % partner.display_name
            )
        message = self._whatsapp_message_for_purchase_order(include_pdf_link=True)
        self._whatsapp_log_outbound(phone, message)
        return self._whatsapp_act_url(phone, message)

    def _can_send_whatsapp(self):
        self.ensure_one()
        if self.state == 'cancel':
            return False
        return bool(self._whatsapp_phone_from_partner(self.partner_id))
