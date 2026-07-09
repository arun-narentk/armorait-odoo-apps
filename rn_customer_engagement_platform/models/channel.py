# -*- coding: utf-8 -*-
"""Customer engagement channels."""

from odoo import fields, models


class RnCustomerEngagementChannel(models.Model):
    _name = 'rn.customer.engagement.channel'
    _description = 'Customer Engagement Channel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channel_type = fields.Selection(
        selection=[
            ('website', 'Website'),
            ('whatsapp', 'WhatsApp'),
            ('telegram', 'Telegram'),
            ('email', 'Email'),
            ('voice', 'Voice'),
            ('mobile_app', 'Mobile App'),
        ],
        required=True,
        default='website',
        tracking=True,
    )
    authentication_mode = fields.Selection(
        selection=[
            ('portal_login', 'Portal Login'),
            ('otp_mobile', 'OTP Mobile'),
            ('otp_email', 'OTP Email'),
            ('order_phone', 'Order Number and Phone'),
            ('oauth', 'OAuth'),
        ],
        required=True,
        default='portal_login',
    )
    status = fields.Selection([('draft', 'Draft'), ('connected', 'Connected'), ('error', 'Error')], default='draft')
    session_count = fields.Integer(compute='_compute_session_count')

    def _compute_session_count(self):
        grouped = self.env['rn.customer.engagement.session']._read_group(
            [('channel_id', 'in', self.ids)], ['channel_id'], ['__count']
        )
        counts = {channel.id: count for channel, count in grouped}
        for record in self:
            record.session_count = counts.get(record.id, 0)
