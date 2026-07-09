# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewellerySettings(models.Model):
    _name = 'rn.jewellery.settings'
    _description = 'Jewellery Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    default_wastage_pct = fields.Float(default=3.0)
    auto_price_from_rate = fields.Boolean(default=True)
    require_hallmark = fields.Boolean(default=True)
    ai_pricing = fields.Boolean(default=True)
    ai_fraud_detection = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one jewellery settings record per company.'),
    ]
