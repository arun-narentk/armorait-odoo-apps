# -*- coding: utf-8 -*-
"""Venue master helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHallVenueService(models.AbstractModel):
    """Shared helpers for hall foundation operations."""

    _name = 'rn.hall.venue.service'
    _description = 'Hall Venue Service'

    def get_default_venue(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.hall.settings'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )
        if settings and settings.default_venue_id:
            return settings.default_venue_id
        return self.env['rn.hall.venue'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )

    def ensure_default_settings(self, company_id=None):
        company_id = company_id or self.env.company.id
        Settings = self.env['rn.hall.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'Hall Settings',
                'company_id': company_id,
            })
        return settings
