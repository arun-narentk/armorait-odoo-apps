# -*- coding: utf-8 -*-
"""Notification stubs for rental lifecycle."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRentalNotificationService(models.AbstractModel):
    """Queue booking notifications."""

    _name = 'rn.rental.notification.service'
    _description = 'Rental Notification Service'

    def notify_reserved(self, booking):
        booking.ensure_one()
        booking.message_post(body='Reservation notification queued.')
        return True

    def notify_confirmed(self, booking):
        booking.ensure_one()
        booking.message_post(body='Confirmation notification queued.')
        return True
