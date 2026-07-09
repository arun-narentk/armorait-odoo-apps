# -*- coding: utf-8 -*-
"""SaaS edition tracking for Dashboard Basic / Pro / Enterprise."""

from odoo import fields, models


class RnDashboardSubscription(models.Model):
    """Commercial tier metadata for ARMORA Dashboard SaaS."""

    _name = 'rn.dashboard.subscription'
    _description = 'Dashboard Subscription'
    _order = 'id desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('basic', 'Dashboard Basic'),
            ('pro', 'Dashboard Pro'),
            ('enterprise', 'Dashboard Enterprise'),
        ],
        default='basic',
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
    monthly_price = fields.Float(
        help='Reference list price: Basic 29, Pro 79, Enterprise 199+ USD.',
    )
    seats = fields.Integer(default=5)
    date_start = fields.Date()
    date_end = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
