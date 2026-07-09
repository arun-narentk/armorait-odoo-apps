# -*- coding: utf-8 -*-
"""Branch / outlet under a restaurant."""

from odoo import api, fields, models


class RnRestaurantBranch(models.Model):
    """Physical or cloud kitchen outlet."""

    _name = 'rn.restaurant.branch'
    _description = 'Restaurant Branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    restaurant_id = fields.Many2one('rn.restaurant', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', string='Address / Contact')
    phone = fields.Char()
    email = fields.Char()
    is_cloud_kitchen = fields.Boolean(string='Cloud Kitchen Only')
    opens_at = fields.Float(string='Opens At', help='Hour as float, e.g. 9.5 = 09:30')
    closes_at = fields.Float(string='Closes At')
    company_id = fields.Many2one(
        related='restaurant_id.company_id',
        store=True,
        index=True,
    )
    floor_ids = fields.One2many('rn.restaurant.floor', 'branch_id', string='Dining Areas')
    table_ids = fields.One2many('rn.restaurant.table', 'branch_id', string='Tables')
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.restaurant.branch') or 'New'
        return super().create(vals_list)
