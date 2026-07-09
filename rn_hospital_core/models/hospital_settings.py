# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalSettings(models.Model):
    _name = 'rn.hospital.settings'
    _description = 'Hospital Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    uhid_prefix = fields.Char(default='UHID', string='UHID Prefix')
    token_reset_daily = fields.Boolean(default=True, string='Reset OPD Tokens Daily')
    ai_scribe_enabled = fields.Boolean(default=True, string='AI Medical Scribe')
    ai_prescription_hints = fields.Boolean(default=True, string='AI Prescription Hints')
    require_consent_on_admission = fields.Boolean(default=True)
    default_consultation_product_id = fields.Many2one('product.product')
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one hospital settings record per company.'),
    ]
