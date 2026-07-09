# -*- coding: utf-8 -*-
"""Festival calendar helpers."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnTempleFestivalService(models.AbstractModel):
    """Upcoming festival queries for dashboard and portal."""

    _name = 'rn.temple.festival.service'
    _description = 'Temple Festival Service'

    def get_upcoming_festivals(self, company_id=None, days=90, limit=20):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        end = today + timedelta(days=days)
        festivals = self.env['rn.temple.festival'].search([
            ('company_id', '=', company_id),
            ('date_start', '>=', today),
            ('date_start', '<=', end),
            ('state', 'in', ('draft', 'confirmed', 'ongoing')),
        ], order='date_start', limit=limit)
        return [{
            'id': fest.id,
            'name': fest.name,
            'date_start': fields.Date.to_string(fest.date_start),
            'date_end': fields.Date.to_string(fest.date_end) if fest.date_end else False,
            'temple': fest.temple_id.name,
            'branch': fest.branch_id.name or '',
            'state': fest.state,
        } for fest in festivals]
