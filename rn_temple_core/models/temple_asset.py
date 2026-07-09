# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleAsset(models.Model):
    _name = 'rn.temple.asset'
    _description = 'Temple Asset'
    _order = 'name'

    name = fields.Char(required=True)
    asset_type = fields.Selection(
        [
            ('building', 'Building'),
            ('land', 'Land'),
            ('vehicle', 'Vehicle'),
            ('jewelry', 'Jewelry'),
            ('equipment', 'Equipment'),
            ('ritual', 'Ritual Item'),
            ('other', 'Other'),
        ],
        default='other',
        required=True,
    )
    location = fields.Char()
    value = fields.Float()
    maintenance_due = fields.Date()
    note = fields.Text()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
