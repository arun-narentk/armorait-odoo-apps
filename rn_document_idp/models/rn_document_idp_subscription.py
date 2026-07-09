# -*- coding: utf-8 -*-
"""SaaS subscription tiers for document volume."""

from odoo import fields, models


class RnDocumentIdpSubscription(models.Model):
    _name = 'rn.document.idp.subscription'
    _description = 'IDP Subscription'
    _order = 'sequence'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    code = fields.Selection(
        selection=[
            ('starter', 'Starter'),
            ('business', 'Business'),
            ('enterprise', 'Enterprise'),
        ],
        required=True,
    )
    monthly_documents = fields.Integer(string='Documents / Month')
    price_inr = fields.Float(string='Price INR / Month')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
