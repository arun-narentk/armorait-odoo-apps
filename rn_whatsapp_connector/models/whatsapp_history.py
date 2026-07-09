# -*- coding: utf-8 -*-
"""Message history and audit trail."""

from odoo import fields, models


class RnWhatsappHistory(models.Model):
    """Immutable-style history entries for message lifecycle events."""

    _name = 'rn.whatsapp.history'
    _description = 'WhatsApp Message History'
    _order = 'create_date desc'

    message_id = fields.Many2one(
        'rn.whatsapp.message',
        string='Message',
        required=True,
        ondelete='cascade',
        index=True,
    )
    event_type = fields.Selection(
        selection=[
            ('created', 'Created'),
            ('queued', 'Queued'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('read', 'Read'),
            ('failed', 'Failed'),
            ('webhook', 'Webhook'),
            ('retry', 'Retry'),
        ],
        required=True,
    )
    description = fields.Text()
    payload = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        related='message_id.company_id',
        store=True,
    )
