# -*- coding: utf-8 -*-
"""Knowledge snippets used by the engagement assistant."""

from odoo import fields, models


class RnCustomerEngagementKnowledge(models.Model):
    _name = 'rn.customer.engagement.knowledge'
    _description = 'Customer Engagement Knowledge'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    category = fields.Selection([('policy', 'Policy'), ('product', 'Product'), ('support', 'Support'), ('billing', 'Billing')], default='support', required=True)
    keyword_hint = fields.Char()
    content = fields.Text(required=True)
