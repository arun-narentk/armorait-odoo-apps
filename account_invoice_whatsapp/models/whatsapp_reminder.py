# -*- coding: utf-8 -*-

from urllib.parse import quote

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WhatsAppReminder(models.Model):
    _name = 'whatsapp.reminder'
    _description = 'WhatsApp Follow-up / Reminder'
    _order = 'scheduled_date asc, id desc'

    res_model = fields.Char(string='Related Model', required=True, index=True)
    res_id = fields.Integer(string='Related Document ID', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Contact', required=True, ondelete='cascade')
    reminder_type = fields.Selection(
        [
            ('invoice_followup', 'Unpaid Invoice Follow-up'),
            ('payment_reminder', 'Payment Reminder'),
            ('sales_followup', 'Sales Follow-up'),
            ('delivery_alert', 'Delivery Status Alert'),
        ],
        string='Type',
        required=True,
        index=True,
    )
    state = fields.Selection(
        [('pending', 'Pending'), ('sent', 'Sent'), ('cancelled', 'Cancelled')],
        string='Status',
        default='pending',
        required=True,
        index=True,
    )
    scheduled_date = fields.Datetime(string='Scheduled', required=True, default=fields.Datetime.now)
    message_text = fields.Text(string='Message')
    sent_at = fields.Datetime(string='Sent At', readonly=True)
    mail_message_id = fields.Many2one('mail.message', string='Chatter Message', readonly=True, ondelete='set null')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def _get_record(self):
        self.ensure_one()
        return self.env[self.res_model].browse(self.res_id).exists()

    def action_open_document(self):
        self.ensure_one()
        record = self._get_record()
        if not record:
            raise UserError(_('Related document no longer exists.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_phone(self):
        self.ensure_one()
        mixin = self.env.get('whatsapp.mixin')
        if mixin:
            return mixin._whatsapp_phone_from_partner(self.partner_id)
        raw = getattr(self.partner_id, 'mobile', None) or self.partner_id.phone or ''
        if not raw:
            return None
        import re
        digits = re.sub(r'\D', '', raw)
        return digits if len(digits) >= 8 else None

    def action_send_whatsapp(self):
        """Open wa.me and mark as sent; log to document chatter."""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending reminders can be sent.'))
        phone = self._get_phone()
        if not phone:
            raise UserError(
                _('No WhatsApp number for %s. Set Phone or Mobile on the contact.') % self.partner_id.display_name
            )
        record = self._get_record()
        if not record:
            raise UserError(_('Related document no longer exists.'))
        message = self.message_text or _('Please check the related document for details.')
        if hasattr(record, '_whatsapp_log_outbound'):
            record._whatsapp_log_outbound(phone, message)
        self.write({
            'state': 'sent',
            'sent_at': fields.Datetime.now(),
        })
        url = 'https://wa.me/%s?text=%s' % (phone, quote(message))
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}

    def action_cancel(self):
        return self.write({'state': 'cancelled'})

    @api.model
    def _cron_whatsapp_reminders(self):
        """Create pending WhatsApp reminders for unpaid invoices, sales follow-up, and (delivery is done in picking write)."""
        today = fields.Date.context_today(self)
        for company in self.env['res.company'].search([]):
            if company.whatsapp_invoice_followup or company.whatsapp_payment_reminder:
                self._create_invoice_reminders(company, today)
            if company.whatsapp_sales_followup:
                self._create_sales_followup_reminders(company, today)

    @api.model
    def _create_invoice_reminders(self, company, today):
        from datetime import timedelta
        days = company.whatsapp_invoice_followup_days or 1
        due_limit = today - timedelta(days=days)
        domain = [
            ('company_id', '=', company.id),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<=', due_limit),
        ]
        for move in self.env['account.move'].search(domain):
            reminder_type = 'payment_reminder' if move.payment_state == 'partial' else 'invoice_followup'
            if not company.whatsapp_payment_reminder and reminder_type == 'payment_reminder':
                continue
            if not company.whatsapp_invoice_followup and reminder_type == 'invoice_followup':
                continue
            if not self._whatsapp_phone_from_partner(move.partner_id):
                continue
            existing = self.search([
                ('res_model', '=', 'account.move'),
                ('res_id', '=', move.id),
                ('reminder_type', '=', reminder_type),
                ('state', '=', 'pending'),
                ('company_id', '=', company.id),
            ], limit=1)
            if existing:
                continue
            message = move._whatsapp_message_for_invoice(include_pdf_link=True, include_lines=True)
            self.create({
                'res_model': 'account.move',
                'res_id': move.id,
                'partner_id': move.partner_id.id,
                'reminder_type': reminder_type,
                'state': 'pending',
                'scheduled_date': fields.Datetime.now(),
                'message_text': message,
                'company_id': company.id,
            })

    def _whatsapp_phone_from_partner(self, partner):
        if not partner:
            return None
        raw = (getattr(partner, 'mobile', None) or partner.phone or '').strip()
        if not raw:
            return None
        import re
        digits = re.sub(r'\D', '', raw)
        return digits if len(digits) >= 8 else None

    @api.model
    def _create_sales_followup_reminders(self, company, today):
        from datetime import timedelta
        days = company.whatsapp_sales_followup_days or 3
        date_limit = today - timedelta(days=days)
        domain = [
            ('company_id', '=', company.id),
            ('state', '=', 'sent'),
            ('date_order', '<=', date_limit),
        ]
        for order in self.env['sale.order'].search(domain):
            if not self._whatsapp_phone_from_partner(order.partner_id):
                continue
            existing = self.search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('reminder_type', '=', 'sales_followup'),
                ('state', '=', 'pending'),
                ('company_id', '=', company.id),
            ], limit=1)
            if existing:
                continue
            message = order._whatsapp_message_for_sale_order(include_pdf_link=True)
            self.create({
                'res_model': 'sale.order',
                'res_id': order.id,
                'partner_id': order.partner_id.id,
                'reminder_type': 'sales_followup',
                'state': 'pending',
                'scheduled_date': fields.Datetime.now(),
                'message_text': message,
                'company_id': company.id,
            })
