# -*- coding: utf-8 -*-
"""Temple master helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnTempleTempleService(models.AbstractModel):
    """Shared helpers for temple foundation operations."""

    _name = 'rn.temple.temple.service'
    _description = 'Temple Service'

    def get_default_temple(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.temple.settings'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )
        if settings and settings.default_temple_id:
            return settings.default_temple_id
        return self.env['rn.temple.temple'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )

    def ensure_default_settings(self, company_id=None):
        company_id = company_id or self.env.company.id
        Settings = self.env['rn.temple.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'Temple Settings',
                'company_id': company_id,
            })
        return settings
