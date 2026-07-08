# -*- coding: utf-8 -*-
"""Configured payment methods for restaurant billing."""

from odoo import fields, models


class RnRestaurantPaymentMethod(models.Model):
    """Payment channel used by POS and online companions."""

    _name = 'rn.restaurant.payment.method'
    _description = 'Restaurant Payment Method'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    restaurant_id = fields.Many2one('rn.restaurant', required=True, ondelete='cascade', index=True)
    method_type = fields.Selection(
        selection=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('upi', 'UPI'),
            ('wallet', 'Wallet'),
            ('razorpay', 'Razorpay'),
            ('stripe', 'Stripe'),
            ('paypal', 'PayPal'),
            ('other', 'Other'),
        ],
        default='cash',
        required=True,
    )
    is_online = fields.Boolean(string='Online Capable')
    opens_drawer = fields.Boolean(string='Open Cash Drawer')
    company_id = fields.Many2one(
        related='restaurant_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Char()
