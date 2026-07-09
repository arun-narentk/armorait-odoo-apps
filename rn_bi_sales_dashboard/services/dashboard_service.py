# -*- coding: utf-8 -*-
"""Dashboard orchestration and KPI payload builder."""

import logging
from datetime import date, timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBiDashboardService(models.AbstractModel):
    """Assemble dashboard cards, charts, and filters."""

    _name = 'rn.bi.dashboard.service'
    _description = 'BI Dashboard Service'

    def _resolve_dates(self, preset='this_month', date_from=None, date_to=None):
        """Map preset names to concrete dates."""
        today = fields.Date.context_today(self)
        if preset == 'custom' and date_from and date_to:
            return date_from, date_to
        if preset == 'today':
            return today, today
        if preset == 'yesterday':
            y = today - timedelta(days=1)
            return y, y
        if preset == 'last_7':
            return today - timedelta(days=6), today
        if preset == 'last_30':
            return today - timedelta(days=29), today
        if preset == 'last_month':
            first = today.replace(day=1)
            end = first - timedelta(days=1)
            start = end.replace(day=1)
            return start, end
        if preset == 'quarter':
            q = (today.month - 1) // 3
            start = date(today.year, q * 3 + 1, 1)
            return start, today
        if preset == 'year':
            return date(today.year, 1, 1), today
        # this_month default
        return today.replace(day=1), today

    def get_dashboard_data(self, filter_vals=None):
        """Return Phase 1 dashboard payload with cards and chart stubs."""
        filter_vals = filter_vals or {}
        preset = filter_vals.get('date_preset') or 'this_month'
        date_from, date_to = self._resolve_dates(
            preset,
            filter_vals.get('date_from'),
            filter_vals.get('date_to'),
        )
        company_id = filter_vals.get('company_id') or self.env.company.id
        cache_key = 'bi_sales:%s:%s:%s:%s' % (company_id, preset, date_from, date_to)
        settings = self.env['rn.bi.dashboard.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        ttl = settings.cache_ttl_seconds if settings else 120
        cached = self.env['rn.bi.cache.service'].get(cache_key)
        if cached:
            return cached

        domain = [('company_id', '=', company_id)]
        if filter_vals.get('salesperson_ids'):
            domain.append(('user_id', 'in', filter_vals['salesperson_ids']))
        if filter_vals.get('team_ids'):
            domain.append(('team_id', 'in', filter_vals['team_ids']))

        Sale = self.env['rn.bi.sales.service']
        orders = Sale.search_orders(date_from, date_to, domain=domain)
        summary = Sale.summarize_orders(orders)
        quotes = Sale.search_orders(date_from, date_to, domain=domain, states=['draft', 'sent'])
        quote_value = sum(quotes.mapped('amount_untaxed'))

        Lead = self.env['crm.lead']
        won = Lead.search_count([
            ('company_id', '=', company_id),
            ('probability', '=', 100),
            ('date_closed', '>=', date_from),
            ('date_closed', '<=', date_to),
        ]) if 'date_closed' in Lead._fields else Lead.search_count([
            ('company_id', '=', company_id),
            ('probability', '=', 100),
        ])
        lost = Lead.search_count([
            ('company_id', '=', company_id),
            ('active', '=', False),
            ('probability', '=', 0),
        ])

        target = self.env['rn.bi.target.service'].get_current_target(company_id)
        charts = self.env['rn.bi.chart.service'].build_chart_bundle(orders, date_from, date_to)
        forecast = self.env['rn.bi.forecast.service'].forecast_revenue(summary['revenue'], target)

        payload = {
            'filters': {
                'date_preset': preset,
                'date_from': fields.Date.to_string(date_from),
                'date_to': fields.Date.to_string(date_to),
            },
            'cards': {
                'total_revenue': summary['revenue'],
                'orders': summary['orders'],
                'aov': summary['aov'],
                'customers': summary['customers'],
                'quotation_count': len(quotes),
                'quotation_value': quote_value,
                'won_opportunities': won,
                'lost_opportunities': lost,
                'target_amount': target.get('target_amount', 0.0),
                'achievement_pct': target.get('achievement_pct', 0.0),
                'margin': 0.0,
                'gross_profit': 0.0,
            },
            'charts': charts,
            'forecast': forecast,
            'tops': self.env['rn.bi.chart.service'].build_top_lists(orders),
        }
        self.env['rn.bi.cache.service'].set(cache_key, payload, ttl=ttl)
        _logger.info('Built BI sales dashboard company=%s period=%s..%s', company_id, date_from, date_to)
        return payload
