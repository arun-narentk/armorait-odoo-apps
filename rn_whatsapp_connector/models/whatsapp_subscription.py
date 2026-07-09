# -*- coding: utf-8 -*-
"""Commercial edition tracking for WhatsApp Automation Platform."""

from odoo import fields, models


class RnWhatsappSubscription(models.Model):
    """Standard / Professional / Enterprise metadata."""

    _name = 'rn.whatsapp.subscription'
    _description = 'WhatsApp Subscription'
    _order = 'id desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='professional',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial',
        required=True,
    )
    list_price = fields.Float(help='Apps reference: Standard 29.99, Professional 79.99, Enterprise 199.99')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    note = fields.Text()
