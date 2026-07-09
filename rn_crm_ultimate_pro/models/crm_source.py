# -*- coding: utf-8 -*-
"""Extra analytics fields for lead sources."""

from odoo import fields, models


class RnCrmSourceAnalytic(models.Model):
    """Tracks conversion metrics per CRM medium/source."""

    _name = 'rn.crm.source.analytic'
    _description = 'CRM Source Analytic'
    _order = 'name'

    name = fields.Char(required=True)
    medium_id = fields.Many2one('utm.medium')
    source_id = fields.Many2one('utm.source')
    lead_count = fields.Integer()
    won_count = fields.Integer()
    conversion_rate = fields.Float(digits=(16, 2))
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
