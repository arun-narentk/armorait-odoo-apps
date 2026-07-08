# -*- coding: utf-8 -*-
"""Rentable asset master."""

from odoo import api, fields, models


class RnRentalAsset(models.Model):
    """Industry-agnostic rentable asset."""

    _name = 'rn.rental.asset'
    _description = 'Rental Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New', tracking=True)
    active = fields.Boolean(default=True)
    category_id = fields.Many2one('rn.rental.category', required=True, index=True)
    product_id = fields.Many2one('product.product', string='Linked Product')
    barcode = fields.Char(index=True)
    serial_number = fields.Char(index=True)
    replacement_cost = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('booked', 'Booked'),
            ('picked_up', 'Picked Up'),
            ('in_use', 'In Use'),
            ('maintenance', 'Maintenance'),
            ('cleaning', 'Cleaning'),
            ('inspection', 'Inspection'),
            ('damaged', 'Damaged'),
            ('lost', 'Lost'),
            ('retired', 'Retired'),
        ],
        default='available',
        required=True,
        tracking=True,
        index=True,
    )
    location = fields.Char(string='Location / Branch')
    owner_id = fields.Many2one('res.partner', string='Owner')
    image_1920 = fields.Image()
    specifications = fields.Html()
    hourly_price = fields.Monetary(currency_field='currency_id')
    half_day_price = fields.Monetary(currency_field='currency_id')
    daily_price = fields.Monetary(currency_field='currency_id')
    weekly_price = fields.Monetary(currency_field='currency_id')
    monthly_price = fields.Monetary(currency_field='currency_id')
    yearly_price = fields.Monetary(currency_field='currency_id')
    deposit_amount = fields.Monetary(currency_field='currency_id')
    pricing_ids = fields.One2many('rn.rental.pricing', 'asset_id', string='Pricing Rules')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.rental.asset') or 'New'
        return super().create(vals_list)

    def action_set_available(self):
        self.write({'state': 'available'})
        return True

    def action_set_maintenance(self):
        self.write({'state': 'maintenance'})
        return True
