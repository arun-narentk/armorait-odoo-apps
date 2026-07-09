# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryItemSpec(models.Model):
    _name = 'rn.jewellery.item.spec'
    _description = 'Jewellery Item Specification'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Product', index=True)
    barcode = fields.Char(index=True)
    metal_type = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum'), ('mixed', 'Mixed')],
        default='gold',
    )
    purity_id = fields.Many2one('rn.jewellery.metal.purity', string='Purity')
    gross_weight = fields.Float(string='Gross Weight (g)', digits=(16, 3))
    net_weight = fields.Float(string='Net Weight (g)', digits=(16, 3))
    stone_weight = fields.Float(string='Stone Weight (ct)', digits=(16, 3))
    diamond_spec = fields.Char(string='Diamond Spec')
    gemstone_spec = fields.Char(string='Gemstone Spec')
    making_charge = fields.Float(string='Making Charge')
    making_charge_type = fields.Selection(
        [('fixed', 'Fixed'), ('per_gram', 'Per Gram'), ('percentage', '% of Metal')],
        default='per_gram',
    )
    wastage_pct = fields.Float(string='Wastage %', default=0.0)
    hallmark_number = fields.Char(index=True)
    design_code = fields.Char()
    collection = fields.Char()
    branch_warehouse_id = fields.Many2one('stock.warehouse', string='Branch')
    list_price_computed = fields.Float(compute='_compute_list_price', store=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('net_weight', 'making_charge', 'making_charge_type', 'metal_type', 'purity_id')
    def _compute_list_price(self):
        Rate = self.env['rn.jewellery.metal.rate']
        for item in self:
            price = 0.0
            rate = Rate.get_latest_rate(item.metal_type, item.company_id.id)
            fine_weight = (item.net_weight or 0.0) * (item.purity_id.purity_factor if item.purity_id else 1.0)
            metal_value = fine_weight * (rate or 0.0)
            making = item.making_charge or 0.0
            if item.making_charge_type == 'per_gram':
                making = making * (item.net_weight or 0.0)
            elif item.making_charge_type == 'percentage':
                making = metal_value * (making / 100.0)
            price = metal_value + making
            item.list_price_computed = round(price, 2)
