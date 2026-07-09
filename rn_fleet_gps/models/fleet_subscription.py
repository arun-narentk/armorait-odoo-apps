# -*- coding: utf-8 -*-
"""Fleet suite commercial edition tracking."""

from odoo import fields, models


class RnFleetSubscription(models.Model):
    _name = 'rn.fleet.subscription'
    _description = 'Fleet Subscription'
    _order = 'id desc'

    name = fields.Char(required=True)
    plan = fields.Selection(
        selection=[
            ('base', 'Fleet GPS Base'),
            ('bundle', 'Complete Fleet Suite'),
        ],
        default='base',
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
    vehicle_limit = fields.Integer(default=25)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
