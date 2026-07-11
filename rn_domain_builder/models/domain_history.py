# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDomainHistory(models.Model):
    _name = 'rn.domain.history'
    _description = 'Domain Builder History'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    res_model = fields.Char(required=True, index=True)
    description = fields.Text(required=True)
    domain_text = fields.Text(required=True)
    record_count = fields.Integer()
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )
    filter_id = fields.Many2one('ir.filters', string='Saved Filter', ondelete='set null')
