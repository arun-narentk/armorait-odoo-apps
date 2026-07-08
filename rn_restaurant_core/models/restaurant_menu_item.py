# -*- coding: utf-8 -*-
"""Sellable menu item linked to product.template optionally."""

from odoo import api, fields, models


class RnRestaurantMenuItem(models.Model):
    """Menu SKU used later by POS, QR, and online ordering."""

    _name = 'rn.restaurant.menu.item'
    _description = 'Restaurant Menu Item'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    restaurant_id = fields.Many2one('rn.restaurant', required=True, ondelete='cascade', index=True)
    category_id = fields.Many2one('rn.restaurant.menu.category', required=True, ondelete='restrict', index=True)
    product_id = fields.Many2one('product.product', string='Linked Product')
    barcode = fields.Char(index=True)
    description = fields.Html()
    list_price = fields.Monetary(currency_field='currency_id', required=True, default=0.0)
    currency_id = fields.Many2one(
        related='restaurant_id.currency_id',
        store=True,
    )
    tax_ids = fields.Many2many(
        'rn.restaurant.tax',
        'rn_restaurant_menu_item_tax_rel',
        'item_id',
        'tax_id',
        string='Taxes',
    )
    is_veg = fields.Boolean(string='Vegetarian')
    is_vegan = fields.Boolean(string='Vegan')
    spice_level = fields.Selection(
        selection=[
            ('none', 'None'),
            ('mild', 'Mild'),
            ('medium', 'Medium'),
            ('hot', 'Hot'),
        ],
        default='none',
    )
    preparation_minutes = fields.Integer(default=10)
    kitchen_station = fields.Selection(
        selection=[
            ('grill', 'Grill'),
            ('fry', 'Fry'),
            ('cold', 'Cold / Salad'),
            ('beverage', 'Beverage'),
            ('dessert', 'Dessert'),
            ('bakery', 'Bakery'),
            ('general', 'General'),
        ],
        default='general',
    )
    available_dine_in = fields.Boolean(default=True)
    available_takeaway = fields.Boolean(default=True)
    available_delivery = fields.Boolean(default=True)
    available_online = fields.Boolean(default=True)
    image_1920 = fields.Image()
    company_id = fields.Many2one(
        related='restaurant_id.company_id',
        store=True,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('out', 'Out of Stock'),
            ('seasonal', 'Seasonal'),
            ('archived', 'Archived'),
        ],
        default='available',
        tracking=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.restaurant.menu.item') or 'New'
        return super().create(vals_list)

    def action_mark_available(self):
        self.write({'state': 'available'})
        return True

    def action_mark_out(self):
        self.write({'state': 'out'})
        return True
