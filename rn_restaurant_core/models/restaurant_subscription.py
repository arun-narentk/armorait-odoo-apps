# -*- coding: utf-8 -*-
"""SaaS plan tracking for Restaurant Cloud POS."""

from odoo import fields, models


class RnRestaurantSubscription(models.Model):
    """Starter / Professional / Enterprise edition metadata."""

    _name = 'rn.restaurant.subscription'
    _description = 'Restaurant Subscription'
    _order = 'id desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='starter',
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
    outlet_limit = fields.Integer(default=1)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    note = fields.Text()
