# -*- coding: utf-8 -*-
from odoo import fields, models


class FilterHistory(models.Model):
    _name = 'rn.filter.history'
    _description = 'Filter Usage History'
    _order = 'used_at desc, id desc'

    filter_id = fields.Many2one('ir.filters', required=True, ondelete='cascade', index=True)
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    model_id = fields.Char(required=True, index=True)
    used_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    source = fields.Selection(
        [('search', 'Search Bar'), ('manager', 'Filter Manager'), ('api', 'API')],
        default='manager',
        required=True,
    )
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, index=True)
