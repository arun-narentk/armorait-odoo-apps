# -*- coding: utf-8 -*-
"""Lightweight public/health + authenticated availability API."""

from odoo import http
from odoo.http import request


class RnDashboardApiController(http.Controller):

    @http.route('/rn_dashboard_core/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'ok': True, 'module': 'rn_dashboard_core'})

    @http.route('/api/rn_dashboard/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, dashboard_id=None, filter_vals=None):
        data = request.env['rn.dashboard.service'].get_dashboard_data(
            dashboard_id=dashboard_id,
            filter_vals=filter_vals or {},
        )
        return {'ok': True, 'data': data}

    @http.route('/api/rn_dashboard/v1/alerts', type='json', auth='user')
    def api_alerts(self, company_id=None):
        alerts = request.env['rn.dashboard.alert.service'].open_alerts(company_id)
        return {
            'ok': True,
            'data': [{
                'id': a.id,
                'name': a.name,
                'severity': a.severity,
                'state': a.state,
            } for a in alerts],
        }
