# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewelleryMetalPurity(models.Model):
    _name = 'rn.jewellery.metal.purity'
    _description = 'Metal Purity'
    _order = 'metal_type, karat desc'

    name = fields.Char(required=True)
    metal_type = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum')],
        required=True,
    )
    karat = fields.Char(string='Karat / Grade', help='e.g. 22K, 18K, 925')
    purity_factor = fields.Float(
        string='Purity Factor',
        digits=(16, 6),
        help='Fine metal ratio, e.g. 0.916 for 22K gold',
    )
    active = fields.Boolean(default=True)
