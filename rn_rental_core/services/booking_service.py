# -*- coding: utf-8 -*-
"""Booking reserve / confirm / cancel orchestration."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRentalBookingService(models.AbstractModel):
    """High-level booking lifecycle for the rental core."""

    _name = 'rn.rental.booking.service'
    _description = 'Rental Booking Service'

    def reserve(self, bookings):
        self.env['rn.rental.availability.service'].validate_booking(bookings)
        self.env['rn.rental.pricing.service'].recompute_booking(bookings)
        for booking in bookings:
            booking.state = 'reserved'
            booking.line_ids.mapped('asset_id').write({'state': 'reserved'})
            self.env['rn.rental.notification.service'].notify_reserved(booking)
        _logger.info('Reserved %s bookings', len(bookings))
        return True

    def confirm(self, bookings):
        self.env['rn.rental.availability.service'].validate_booking(bookings)
        self.env['rn.rental.pricing.service'].recompute_booking(bookings)
        for booking in bookings:
            booking.state = 'confirmed'
            booking.line_ids.mapped('asset_id').write({'state': 'booked'})
            self.env['rn.rental.notification.service'].notify_confirmed(booking)
        return True

    def cancel(self, bookings):
        for booking in bookings:
            booking.state = 'cancel'
            for line in booking.line_ids:
                if line.asset_id.state in ('reserved', 'booked'):
                    line.asset_id.state = 'available'
        return True
