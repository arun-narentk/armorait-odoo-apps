# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ['product.template', 'rn.name.mixin']

    rn_brand = fields.Char(string='Brand')
    rn_series = fields.Char(string='Series')
    rn_model_number = fields.Char(string='Model')
    rn_color = fields.Char(string='Color')
    rn_capacity = fields.Char(string='Capacity')
    rn_material = fields.Char(string='Material')
    rn_variant_label = fields.Char(string='Variant')
    rn_size = fields.Char(string='Size')
