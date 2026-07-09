# -*- coding: utf-8 -*-
"""Annual maintenance contract visibility for customers."""

from odoo import fields, models


class RnCustomerExperienceAmc(models.Model):
    _name = 'rn.customer.experience.amc'
    _description = 'Experience AMC Contract'
    _order = 'renewal_date'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True, index=True)
    start_date = fields.Date()
    end_date = fields.Date()
    renewal_date = fields.Date(index=True)
    next_visit_date = fields.Date()
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('expiring', 'Expiring Soon'),
            ('expired', 'Expired'),
            ('renewed', 'Renewed'),
        ],
        default='active',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    service_history = fields.Text()
