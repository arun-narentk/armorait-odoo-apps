# -*- coding: utf-8 -*-
"""Webhook log model."""

from odoo import fields, models


class RnWhatsappWebhook(models.Model):
    """Stores raw webhook payloads for auditing and replay."""

    _name = 'rn.whatsapp.webhook'
    _description = 'WhatsApp Webhook Log'
    _order = 'create_date desc'

    name = fields.Char(default='Webhook Event', required=True)
    provider = fields.Selection(
        selection=[
            ('meta_cloud', 'Meta Cloud API'),
            ('twilio', 'Twilio'),
            ('dialog360', '360Dialog'),
            ('gupshup', 'Gupshup'),
            ('interakt', 'Interakt'),
            ('chat_api', 'Chat API'),
            ('ultramsg', 'UltraMsg'),
            ('green_api', 'Green API'),
        ],
        required=True,
    )
    account_id = fields.Many2one('rn.whatsapp.account', string='Account', ondelete='set null')
    headers = fields.Text()
    payload = fields.Text()
    response = fields.Text()
    status = fields.Selection(
        selection=[
            ('received', 'Received'),
            ('processed', 'Processed'),
            ('failed', 'Failed'),
            ('ignored', 'Ignored'),
        ],
        default='received',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
