# -*- coding: utf-8 -*-
"""Restaurant brand / outlet group configuration."""

from odoo import api, fields, models


class RnRestaurant(models.Model):
    """Top-level restaurant configuration for multi-branch SaaS."""

    _name = 'rn.restaurant'
    _description = 'Restaurant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Legal Entity')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    branch_ids = fields.One2many('rn.restaurant.branch', 'restaurant_id', string='Branches')
    menu_category_ids = fields.One2many('rn.restaurant.menu.category', 'restaurant_id', string='Menu Categories')
    tax_ids = fields.One2many('rn.restaurant.tax', 'restaurant_id', string='Taxes')
    payment_method_ids = fields.One2many('rn.restaurant.payment.method', 'restaurant_id', string='Payment Methods')
    cuisine_type = fields.Selection(
        selection=[
            ('restaurant', 'Restaurant'),
            ('cafe', 'Cafe'),
            ('bakery', 'Bakery'),
            ('cloud_kitchen', 'Cloud Kitchen'),
            ('hotel', 'Hotel Dining'),
            ('food_truck', 'Food Truck'),
            ('other', 'Other'),
        ],
        default='restaurant',
        required=True,
        tracking=True,
    )
    timezone = fields.Char(default='Asia/Kolkata')
    note = fields.Html()
    branch_count = fields.Integer(compute='_compute_counts')
    table_count = fields.Integer(compute='_compute_counts')
    item_count = fields.Integer(compute='_compute_counts')

    @api.depends('branch_ids', 'menu_category_ids')
    def _compute_counts(self):
        Table = self.env['rn.restaurant.table']
        Item = self.env['rn.restaurant.menu.item']
        for restaurant in self:
            restaurant.branch_count = len(restaurant.branch_ids)
            restaurant.table_count = Table.search_count([('restaurant_id', '=', restaurant.id)])
            restaurant.item_count = Item.search_count([('restaurant_id', '=', restaurant.id)])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.restaurant') or 'New'
        return super().create(vals_list)

    def action_view_branches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branches',
            'res_model': 'rn.restaurant.branch',
            'view_mode': 'list,form',
            'domain': [('restaurant_id', '=', self.id)],
            'context': {'default_restaurant_id': self.id},
        }

    def action_view_tables(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tables',
            'res_model': 'rn.restaurant.table',
            'view_mode': 'list,kanban,form',
            'domain': [('restaurant_id', '=', self.id)],
            'context': {'default_restaurant_id': self.id},
        }

    def action_view_menu_items(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Menu Items',
            'res_model': 'rn.restaurant.menu.item',
            'view_mode': 'list,kanban,form',
            'domain': [('restaurant_id', '=', self.id)],
            'context': {'default_restaurant_id': self.id},
        }
