# -*- coding: utf-8 -*-
"""WhatsApp message model."""

import uuid

from odoo import api, fields, models


class RnWhatsappMessage(models.Model):
    """Represents an outbound or inbound WhatsApp message."""

    _name = 'rn.whatsapp.message'
    _description = 'WhatsApp Message'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

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
    )
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    phone = fields.Char(string='Phone', required=True, tracking=True)
    message_type = fields.Selection(
        selection=[
            ('text', 'Plain Text'),
            ('template', 'Template'),
            ('image', 'Image'),
            ('video', 'Video'),
            ('document', 'Document'),
            ('location', 'Location'),
            ('interactive', 'Interactive Button'),
            ('list', 'List Message'),
            ('reaction', 'Reaction'),
        ],
        default='text',
        required=True,
    )
    body = fields.Text(string='Text')
    template_id = fields.Many2one('rn.whatsapp.template', string='Template')
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
        selection=[('outbound', 'Outbound'), ('inbound', 'Inbound')],
        default='outbound',
        required=True,
    )
    provider_message_id = fields.Char(string='Provider Message ID', copy=False, index=True)
    error_message = fields.Text(string='Error')
    retry_count = fields.Integer(default=0)
    sent_at = fields.Datetime(string='Sent Time')
    delivered_at = fields.Datetime(string='Delivered Time')
    read_at = fields.Datetime(string='Read Time')
    failed_at = fields.Datetime(string='Failed Time')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    priority = fields.Selection(
        selection=[('0', 'Normal'), ('1', 'High')],
        default='0',
    )
    schedule_at = fields.Datetime(string='Schedule Time')
    res_model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)

    _uuid_company_uniq = models.Constraint(
        'unique(uuid, company_id)',
        'Message UUID must be unique per company.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure each message has a UUID before persistence."""
        for vals in vals_list:
            if not vals.get('uuid'):
                vals['uuid'] = str(uuid.uuid4())
        return super().create(vals_list)

    def action_queue_message(self):
        """Queue the message for sending (Phase 4)."""
        for message in self:
            if message.status == 'draft':
                message.status = 'queued'
        return True
