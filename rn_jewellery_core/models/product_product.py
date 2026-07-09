# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    jewellery_spec_id = fields.Many2one('rn.jewellery.item.spec', string='Jewellery Spec')
