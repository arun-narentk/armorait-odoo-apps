# -*- coding: utf-8 -*-
"""WhatsApp message / queue model."""

import uuid

from odoo import api, fields, models


class RnWhatsappMessage(models.Model):
    """Outbound or inbound WhatsApp message (also acts as queue row)."""

    _name = 'rn.whatsapp.message'
    _description = 'WhatsApp Message'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(default='New', copy=False, index=True)
    uuid = fields.Char(
        string='UUID',
        default=lambda self: str(uuid.uuid4()),
        required=True,
        copy=False,
        index=True,
    )
    account_id = fields.Many2one(
        'rn.whatsapp.account',
        string='Account',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    phone = fields.Char(string='Recipient', required=True, tracking=True)
    message_type = fields.Selection(
        selection=[
            ('text', 'Text'),
            ('template', 'Template'),
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('document', 'PDF / Document'),
            ('location', 'Location'),
            ('contact', 'Contact'),
            ('sticker', 'Sticker'),
            ('interactive', 'Interactive Buttons'),
            ('list', 'List Message'),
            ('cta', 'CTA Buttons'),
            ('catalog', 'Product Catalog'),
            ('product', 'Product Message'),
        ],
        default='text',
        required=True,
    )
    body = fields.Text(string='Message')
    template_id = fields.Many2one('rn.whatsapp.template', string='Template')
    template_vars = fields.Text(string='Template Variables (JSON)')
    attachment_ids = fields.One2many('rn.whatsapp.attachment', 'message_id', string='Attachments')
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('queued', 'Queued'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('read', 'Read'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    direction = fields.Selection(
        selection=[('outbound', 'Outgoing'), ('inbound', 'Incoming')],
        default='outbound',
        required=True,
        index=True,
    )
    provider_message_id = fields.Char(string='Provider Message ID', copy=False, index=True)
    provider_response = fields.Text(string='Provider Response')
    error_message = fields.Text(string='Error')
    retry_count = fields.Integer(default=0)
    max_retries = fields.Integer(default=3)
    sent_at = fields.Datetime(string='Sent Time')
    delivered_at = fields.Datetime(string='Delivered Time')
    read_at = fields.Datetime(string='Read Time')
    failed_at = fields.Datetime(string='Failed Time')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    priority = fields.Selection(
        selection=[('0', 'Normal'), ('1', 'High'), ('2', 'Urgent')],
        default='0',
        index=True,
    )
    schedule_at = fields.Datetime(string='Scheduled Time', index=True)
    automation_rule_id = fields.Many2one('rn.whatsapp.automation.rule', string='Automation Rule')
    res_model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)

    _uuid_company_uniq = models.Constraint(
        'unique(uuid, company_id)',
        'Message UUID must be unique per company.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('uuid'):
                vals['uuid'] = str(uuid.uuid4())
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.whatsapp.message') or vals['uuid'][:8]
        return super().create(vals_list)

    def action_queue_message(self):
        for message in self:
            if message.status in ('draft', 'failed'):
                message.write({'status': 'queued', 'error_message': False})
        return True

    def action_send_now(self):
        return self.env['rn.whatsapp.message.service'].send_messages(self)

    def action_cancel(self):
        self.filtered(lambda m: m.status in ('draft', 'queued')).write({'status': 'cancelled'})
        return True
