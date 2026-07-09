# -*- coding: utf-8 -*-
"""Company hall settings."""

from odoo import fields, models


class RnHallSettings(models.Model):
    """Defaults shared across hall companion modules."""

    _name = 'rn.hall.settings'
    _description = 'Hall Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Hall Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_venue_id = fields.Many2one('rn.hall.venue', string='Default Venue')
    venue_label = fields.Char(
        default='Marriage Hall',
        help='UI label override: Marriage Hall, Banquet, Convention Center, etc.',
    )
    customer_label = fields.Char(default='Customer')
    enable_online_booking = fields.Boolean(default=True)
    enable_waitlist = fields.Boolean(default=True)
    enable_conflict_block = fields.Boolean(
        default=True,
        string='Block Confirmed Double Bookings',
    )
    booking_prefix = fields.Char(default='BK')
    receipt_prefix = fields.Char(default='RCP')
    timezone = fields.Char(default='Asia/Kolkata')
    enable_sms = fields.Boolean(default=False)
    enable_whatsapp = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one hall settings record per company.',
    )
