# -*- coding: utf-8 -*-
"""Asset availability and conflict detection."""

import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnRentalAvailabilityService(models.AbstractModel):
    """Check whether assets can be reserved for a period."""

    _name = 'rn.rental.availability.service'
    _description = 'Rental Availability Service'

    BLOCKING_STATES = ('reserved', 'confirmed', 'picked_up')

    def find_conflicts(self, asset, date_start, date_end, exclude_booking=None):
        domain = [
            ('asset_id', '=', asset.id),
            ('booking_id.state', 'in', list(self.BLOCKING_STATES)),
            ('date_start', '<', date_end),
            ('date_end', '>', date_start),
        ]
        if exclude_booking:
            domain.append(('booking_id', '!=', exclude_booking.id))
        return self.env['rn.rental.booking.line'].search(domain)

    def is_available(self, asset, date_start, date_end, exclude_booking=None):
        if asset.state in ('maintenance', 'damaged', 'lost', 'retired'):
            return False
        return not bool(self.find_conflicts(asset, date_start, date_end, exclude_booking=exclude_booking))

    def validate_booking(self, bookings):
        settings = self.env['rn.rental.settings'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )
        block = True if not settings else settings.allow_overlap_block
        for booking in bookings:
            for line in booking.line_ids:
                conflicts = self.find_conflicts(
                    line.asset_id,
                    booking.date_start,
                    booking.date_end,
                    exclude_booking=booking,
                )
                if conflicts and block:
                    raise UserError(
                        'Asset %s is not available from %s to %s.' % (
                            line.asset_id.display_name,
                            booking.date_start,
                            booking.date_end,
                        )
                    )
        _logger.info('Availability validated for %s bookings', len(bookings))
        return True
