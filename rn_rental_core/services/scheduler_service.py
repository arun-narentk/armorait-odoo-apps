# -*- coding: utf-8 -*-
"""Background jobs for rental core."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnRentalSchedulerService(models.AbstractModel):
    """Cron entry points."""

    _name = 'rn.rental.scheduler.service'
    _description = 'Rental Scheduler Service'

    def cron_release_expired_reservations(self):
        """Release reserved assets on cancelled overdue drafts (Phase 1 stub)."""
        now = fields.Datetime.now()
        outdated = self.env['rn.rental.booking'].search([
            ('state', '=', 'reserved'),
            ('date_end', '<', now),
        ])
        if outdated:
            self.env['rn.rental.booking.service'].cancel(outdated)
        _logger.info('Released %s expired reservations', len(outdated))
        return True
