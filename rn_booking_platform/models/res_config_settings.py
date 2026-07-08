# -*- coding: utf-8 -*-
"""Settings app bridge for booking platform."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose booking toggles in Settings."""

    _inherit = 'res.config.settings'

    rn_booking_enabled = fields.Boolean(
        string='Enable Booking Platform',
        config_parameter='rn_booking_platform.enabled',
        default=True,
    )
    rn_booking_slot_interval = fields.Integer(
        string='Slot Interval (minutes)',
        config_parameter='rn_booking_platform.slot_interval',
        default=15,
    )
    rn_booking_guest = fields.Boolean(
        string='Allow Guest Booking',
        config_parameter='rn_booking_platform.allow_guest',
        default=True,
    )
