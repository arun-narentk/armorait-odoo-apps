# -*- coding: utf-8 -*-
"""SaaS-ready subscription / edition metadata per company."""

from odoo import fields, models


class RnHrmsSubscription(models.Model):
    """Tracks which HRMS edition a company is entitled to use."""

    _name = 'rn.hrms.subscription'
    _description = 'HRMS Subscription'
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
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
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
    max_employees = fields.Integer(default=50)
    note = fields.Text()
