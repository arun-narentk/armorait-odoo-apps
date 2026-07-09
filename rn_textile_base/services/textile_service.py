# -*- coding: utf-8 -*-
"""Textile foundation helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnTextileFactoryService(models.AbstractModel):
    """Shared helpers for textile foundation operations."""

    _name = 'rn.textile.factory.service'
    _description = 'Textile Factory Service'

    def get_default_factory(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.textile.settings'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )
        if settings and settings.default_factory_id:
            return settings.default_factory_id
        return self.env['rn.textile.factory'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )

    def ensure_default_settings(self, company_id=None):
        company_id = company_id or self.env.company.id
        Settings = self.env['rn.textile.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'Textile Settings',
                'company_id': company_id,
            })
        return settings

    def get_machine_utilization_summary(self, company_id=None):
        """Simple active vs total machine ratio for dashboard."""
        company_id = company_id or self.env.company.id
        Machine = self.env['rn.textile.machine']
        total = Machine.search_count([('company_id', '=', company_id), ('active', '=', True)])
        active = Machine.search_count([
            ('company_id', '=', company_id),
            ('active', '=', True),
            ('state', '=', 'active'),
        ])
        rate = round((active / total) * 100, 1) if total else 0.0
        return {'total': total, 'active': active, 'utilization_rate': rate}
