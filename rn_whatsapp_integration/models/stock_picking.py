# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'whatsapp.mixin']

    can_send_whatsapp = fields.Boolean(
        string='Can Send via WhatsApp',
        compute='_compute_can_send_whatsapp',
    )

    @api.depends('state', 'partner_id', 'partner_id.phone')
    def _compute_can_send_whatsapp(self):
        for picking in self:
            picking.can_send_whatsapp = picking._can_send_whatsapp()

    def _whatsapp_message_for_delivery(self):
        self.ensure_one()
        parts = [
            _('Hi,'),
            _('Delivery Order: %s') % self.name,
            _('Contact: %s') % (self.partner_id.name or ''),
        ]
        if self.move_ids:
            parts.append('')
            parts.append(_('Products:'))
            for move in self.move_ids.filtered(lambda m: m.product_id):
                name = (move.product_id.display_name or '')[:50]
                parts.append('• %s x %s' % (name, move.product_uom_qty))
        return '\n'.join(parts)

    def action_send_whatsapp(self):
        self.ensure_one()
        if self.state == 'cancel':
            raise UserError(_('Cannot send a cancelled transfer via WhatsApp.'))
        if not self.partner_id:
            raise UserError(_('No contact set on this transfer.'))
        partner = self.partner_id
        phone = self._whatsapp_phone_from_partner(partner)
        if not phone:
            raise UserError(
                _('No WhatsApp number for %s. Please set Mobile or Phone on the contact.')
                % partner.display_name
            )
        message = self._whatsapp_message_for_delivery()
        self._whatsapp_log_outbound(phone, message)
        return self._whatsapp_act_url(phone, message)

    def _can_send_whatsapp(self):
        self.ensure_one()
        if self.state == 'cancel' or not self.partner_id:
            return False
        return bool(self._whatsapp_phone_from_partner(self.partner_id))

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if vals.get('state') == 'done':
            for picking in self:
                if not picking.partner_id or picking.picking_type_code != 'outgoing':
                    continue
                company = picking.company_id
                if not getattr(company, 'whatsapp_delivery_alert', False):
                    continue
                if not picking._whatsapp_phone_from_partner(picking.partner_id):
                    continue
                existing = self.env['whatsapp.reminder'].search([
                    ('res_model', '=', 'stock.picking'),
                    ('res_id', '=', picking.id),
                    ('reminder_type', '=', 'delivery_alert'),
                    ('state', '=', 'pending'),
                    ('company_id', '=', company.id),
                ], limit=1)
                if existing:
                    continue
                message = picking._whatsapp_message_for_delivery()
                self.env['whatsapp.reminder'].create({
                    'res_model': 'stock.picking',
                    'res_id': picking.id,
                    'partner_id': picking.partner_id.id,
                    'reminder_type': 'delivery_alert',
                    'state': 'pending',
                    'scheduled_date': fields.Datetime.now(),
                    'message_text': message,
                    'company_id': company.id,
                })
                if hasattr(picking, 'message_post'):
                    picking.message_post(
                        body=_('Delivery validated. WhatsApp status alert suggested for %s.') % picking.partner_id.name,
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
        return res
