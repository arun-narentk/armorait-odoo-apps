# -*- coding: utf-8 -*-
"""Resolve date presets and filter dictionaries."""

from datetime import date, timedelta

from odoo import fields, models


class RnDashboardFilterService(models.AbstractModel):
    """Shared filter resolution for all domain dashboards."""

    _name = 'rn.dashboard.filter.service'
    _description = 'Dashboard Filter Service'

    def resolve_dates(self, preset='today', date_from=None, date_to=None):
        today = fields.Date.context_today(self)
        if preset == 'custom' and date_from and date_to:
            return date_from, date_to
        if preset == 'yesterday':
            y = today - timedelta(days=1)
            return y, y
        if preset == 'last_7':
            return today - timedelta(days=6), today
        if preset == 'last_30':
            return today - timedelta(days=29), today
        if preset == 'this_month':
            return today.replace(day=1), today
        if preset == 'last_month':
            first = today.replace(day=1)
            end = first - timedelta(days=1)
            start = end.replace(day=1)
            return start, end
        if preset == 'this_quarter':
            q = (today.month - 1) // 3
            start = date(today.year, q * 3 + 1, 1)
            return start, today
        if preset == 'this_year':
            return date(today.year, 1, 1), today
        return today, today

    def normalize(self, filter_vals=None, filter_id=None):
        filter_vals = dict(filter_vals or {})
        if filter_id:
            filt = self.env['rn.dashboard.filter'].browse(filter_id)
            if filt.exists():
                base = filt.to_vals()
                base.update({k: v for k, v in filter_vals.items() if v not in (False, None, '')})
                filter_vals = base
        preset = filter_vals.get('date_preset') or 'today'
        date_from, date_to = self.resolve_dates(
            preset,
            filter_vals.get('date_from'),
            filter_vals.get('date_to'),
        )
        filter_vals['date_preset'] = preset
        filter_vals['date_from'] = date_from
        filter_vals['date_to'] = date_to
        filter_vals['company_id'] = filter_vals.get('company_id') or self.env.company.id
        return filter_vals
