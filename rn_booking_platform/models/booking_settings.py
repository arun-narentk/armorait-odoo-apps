# -*- coding: utf-8 -*-
"""Company booking platform settings."""

from odoo import fields, models


class RnBookingSettings(models.Model):
    """Defaults for slots, reminders, and payments."""

    _name = 'rn.booking.settings'
    _description = 'Booking Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Booking Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    industry_id = fields.Many2one('rn.booking.industry')
    slot_interval_minutes = fields.Integer(default=15)
    default_buffer_minutes = fields.Integer(default=0)
    allow_guest_booking = fields.Boolean(default=True)
    require_login = fields.Boolean(default=False)
    advance_payment_required = fields.Boolean(default=False)
    advance_payment_pct = fields.Float(default=100.0)
    reminder_hours = fields.Integer(default=24)
    auto_invoice = fields.Selection(
        selection=[
            ('none', 'Manual'),
            ('on_booking', 'On Booking'),
            ('on_payment', 'After Payment'),
            ('on_done', 'After Appointment'),
        ],
        default='none',
    )
    enable_email = fields.Boolean(default=True)
    enable_sms = fields.Boolean(default=False)
    enable_whatsapp = fields.Boolean(default=False)
    timezone = fields.Char(default='UTC')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one booking settings record per company.',
    )
