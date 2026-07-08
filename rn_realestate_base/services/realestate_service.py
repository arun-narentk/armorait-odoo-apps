# -*- coding: utf-8 -*-
"""Real estate foundation helpers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnRealestateDeveloperService(models.AbstractModel):
    """Shared helpers for real estate foundation operations."""

    _name = 'rn.realestate.developer.service'
    _description = 'Real Estate Developer Service'

    def get_default_developer(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.realestate.settings'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )
        if settings and settings.default_developer_id:
            return settings.default_developer_id
        return self.env['rn.realestate.developer'].search(
            [('company_id', '=', company_id)],
            limit=1,
        )

    def ensure_default_settings(self, company_id=None):
        company_id = company_id or self.env.company.id
        Settings = self.env['rn.realestate.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'Real Estate Settings',
                'company_id': company_id,
            })
        return settings

    def get_inventory_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        Unit = self.env['rn.realestate.unit']
        domain = [('company_id', '=', company_id), ('active', '=', True)]
        total = Unit.search_count(domain)
        available = Unit.search_count(domain + [('status', '=', 'available')])
        booked = Unit.search_count(domain + [('status', '=', 'booked')])
        sold = Unit.search_count(domain + [('status', '=', 'sold')])
        blocked = Unit.search_count(domain + [('status', '=', 'blocked')])
        return {
            'total': total,
            'available': available,
            'booked': booked,
            'sold': sold,
            'blocked': blocked,
            'sell_through': round((sold / total) * 100, 1) if total else 0.0,
        }
