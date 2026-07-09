# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionEquipment(models.Model):
    _name = 'rn.construction.equipment'
    _description = 'Construction Equipment'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    equipment_type = fields.Selection(
        [
            ('excavator', 'Excavator'),
            ('crane', 'Crane'),
            ('truck', 'Truck'),
            ('mixer', 'Mixer'),
            ('generator', 'Generator'),
            ('other', 'Other'),
        ],
        default='other',
    )
    status = fields.Selection(
        [('available', 'Available'), ('in_use', 'In Use'), ('maintenance', 'Maintenance')],
        default='available',
    )
    operator_id = fields.Many2one('hr.employee', string='Operator')
    site_id = fields.Many2one('rn.construction.site')
    usage_ids = fields.One2many('rn.construction.equipment.usage', 'equipment_id')
    fuel_cost_month = fields.Float()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
