# -*- coding: utf-8 -*-
"""Assemble generic dashboard payloads for the OWL shell."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDashboardService(models.AbstractModel):
    """Framework payload builder. Domain modules override via providers later."""

    _name = 'rn.dashboard.service'
    _description = 'Dashboard Service'

    def get_dashboard_data(self, dashboard_id=None, filter_vals=None, filter_id=None):
        Filter = self.env['rn.dashboard.filter.service']
        filter_vals = Filter.normalize(filter_vals, filter_id=filter_id)
        company_id = filter_vals['company_id']
        Dashboard = self.env['rn.dashboard']
        dashboard = Dashboard.browse(dashboard_id) if dashboard_id else Dashboard.search([
            ('company_id', '=', company_id),
            ('is_default', '=', True),
        ], limit=1)
        if not dashboard and dashboard_id:
            dashboard = Dashboard.browse()
        if not dashboard:
            dashboard = Dashboard.search([('company_id', '=', company_id)], limit=1)

        settings = self.env['rn.dashboard.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        ttl = settings.cache_ttl_seconds if settings else 60
        cache_key = 'shell:%s:%s:%s:%s' % (
            company_id,
            dashboard.id if dashboard else 0,
            filter_vals.get('date_preset'),
            filter_vals.get('shift'),
        )
        cached = self.env['rn.dashboard.cache.service'].get(cache_key)
        if cached:
            return cached

        widgets = []
        for widget in dashboard.widget_ids.filtered('active') if dashboard else []:
            widgets.append({
                'id': widget.id,
                'name': widget.name,
                'type': widget.widget_type,
                'kpi_key': widget.kpi_key,
                'size': widget.size,
                'color': widget.color,
            })

        # Framework sample KPIs (domain modules replace via mrp/sales providers)
        kpi_cards = self._sample_kpi_cards(filter_vals)
        Chart = self.env['rn.dashboard.chart.service']
        charts = {
            'trend': Chart.build_line(
                ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                [{'label': 'Output', 'data': [12, 18, 15, 20, 17]}],
                title='Sample Trend',
            ),
            'pareto': Chart.build_pareto(
                ['Setup', 'Material', 'Power', 'Quality', 'Other'],
                [40, 25, 18, 10, 7],
                title='Sample Downtime Pareto',
            ),
            'gauge': Chart.build_gauge(72.5, title='Sample Efficiency'),
        }
        alerts = [{
            'id': a.id,
            'name': a.name,
            'severity': a.severity,
            'kpi_key': a.kpi_key,
            'value': a.value,
        } for a in self.env['rn.dashboard.alert.service'].open_alerts(company_id)]

        payload = {
            'dashboard': {
                'id': dashboard.id if dashboard else False,
                'name': dashboard.name if dashboard else 'ARMORA Dashboard',
                'type': dashboard.dashboard_type if dashboard else 'custom',
                'theme': dashboard.theme if dashboard else 'light',
                'is_tv_mode': bool(dashboard.is_tv_mode) if dashboard else False,
                'refresh_interval': (
                    dashboard.refresh_interval if dashboard
                    else (settings.default_refresh_seconds if settings else 30)
                ),
                'show_logo': bool(dashboard.show_logo) if dashboard else True,
                'show_clock': bool(dashboard.show_clock) if dashboard else True,
                'show_alerts': bool(dashboard.show_alerts) if dashboard else True,
            },
            'filters': filter_vals,
            'widgets': widgets,
            'cards': kpi_cards,
            'charts': charts,
            'alerts': alerts,
            'status_legend': {
                'running': '#16A34A',
                'setup': '#2563EB',
                'idle': '#CA8A04',
                'breakdown': '#DC2626',
                'offline': '#334155',
                'maintenance': '#7C3AED',
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
            'edition': self._edition_label(company_id),
        }
        self.env['rn.dashboard.cache.service'].set(cache_key, payload, ttl_seconds=ttl)
        return payload

    def _sample_kpi_cards(self, filter_vals):
        return {
            'target': 1000,
            'actual': 820,
            'progress_pct': 82.0,
            'efficiency_pct': 78.5,
            'open_alerts': self.env['rn.dashboard.alert'].search_count([
                ('company_id', '=', filter_vals['company_id']),
                ('state', '=', 'open'),
            ]),
            'widgets': self.env['rn.dashboard.widget'].search_count([
                ('company_id', '=', filter_vals['company_id']),
            ]),
        }

    def _edition_label(self, company_id):
        sub = self.env['rn.dashboard.subscription'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ['trial', 'active']),
        ], limit=1)
        return sub.plan if sub else 'basic'
