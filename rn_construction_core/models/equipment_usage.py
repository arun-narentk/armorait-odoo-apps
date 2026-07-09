# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionEquipmentUsage(models.Model):
    _name = 'rn.construction.equipment.usage'
    _description = 'Equipment Usage Log'
    _order = 'usage_date desc'

    equipment_id = fields.Many2one('rn.construction.equipment', required=True, ondelete='cascade', index=True)
    site_id = fields.Many2one('rn.construction.site', required=True)
    usage_date = fields.Date(required=True, default=fields.Date.context_today)
    hours = fields.Float()
    fuel_liters = fields.Float()
    note = fields.Text()
    company_id = fields.Many2one(related='equipment_id.company_id', store=True, index=True)
