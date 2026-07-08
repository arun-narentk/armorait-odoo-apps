# -*- coding: utf-8 -*-
"""SaaS / edition metadata for Hospital ERP."""

from odoo import fields, models


class RnHmsSubscription(models.Model):
    """Tracks which Hospital ERP edition a company uses."""

    _name = 'rn.hms.subscription'
    _description = 'HMS Subscription'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    edition = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('standard', 'Standard'),
            ('professional', 'Professional'),
            ('saas', 'SaaS'),
        ],
        default='starter',
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancel', 'Cancelled'),
        ],
        default='trial',
        tracking=True,
    )
    date_start = fields.Date(default=fields.Date.context_today)
    date_end = fields.Date()
    max_beds = fields.Integer(default=50)
    note = fields.Text()
