# -*- coding: utf-8 -*-
"""Public API stubs for inventory forecasting."""

from odoo import http
from odoo.http import request


class RnInvForecastApiController(http.Controller):
    """API for forecast, analysis, and alerts."""

    @http.route('/api/rn_inventory_forecast/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return {'ok': True, 'data': request.env['rn.inv.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_inventory_forecast/v1/alerts', type='json', auth='user')
    def api_alerts(self, **kwargs):
        alerts = request.env['rn.inv.stock.alert'].search_read(
            [('state', '=', 'open')],
            ['name', 'alert_type', 'severity', 'product_id', 'qty'],
            limit=50,
        )
        return {'ok': True, 'alerts': alerts}

    @http.route('/rn_inventory_forecast/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_inventory_forecast'})
