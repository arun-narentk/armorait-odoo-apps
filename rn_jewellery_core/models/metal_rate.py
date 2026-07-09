# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryMetalRate(models.Model):
    _name = 'rn.jewellery.metal.rate'
    _description = 'Metal Rate'
    _order = 'rate_date desc, id desc'

    metal_type = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum')],
        required=True,
        index=True,
    )
    rate_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    rate_per_gram = fields.Float(required=True, digits=(16, 2), string='Rate per Gram')
    source = fields.Char(string='Source')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        (
            'metal_rate_date_uniq',
            'unique(metal_type, rate_date, company_id)',
            'Only one rate per metal per day per company.',
        ),
    ]

    @api.model
    def get_latest_rate(self, metal_type, company_id=None):
        company_id = company_id or self.env.company.id
        rate = self.search([
            ('metal_type', '=', metal_type),
            ('company_id', '=', company_id),
        ], order='rate_date desc', limit=1)
        return rate.rate_per_gram if rate else 0.0
