# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleSettings(models.Model):
    _name = 'rn.temple.settings'
    _description = 'Temple Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    temple_name = fields.Char()
    enable_online_seva = fields.Boolean(default=True)
    enable_tax_receipts = fields.Boolean(default=True)
    default_seva_capacity = fields.Integer(default=5)
    ai_assistant = fields.Boolean(default=True)
    ai_donation_analytics = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one temple settings record per company.'),
    ]
