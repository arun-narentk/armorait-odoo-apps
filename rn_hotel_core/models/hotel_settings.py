# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelSettings(models.Model):
    _name = 'rn.hotel.settings'
    _description = 'Hotel Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    default_checkin_time = fields.Float(default=14.0, string='Check-in Hour')
    default_checkout_time = fields.Float(default=11.0, string='Check-out Hour')
    auto_dirty_on_checkout = fields.Boolean(default=True)
    ai_pricing_enabled = fields.Boolean(default=True)
    ai_concierge_enabled = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one hotel settings record per company.'),
    ]
