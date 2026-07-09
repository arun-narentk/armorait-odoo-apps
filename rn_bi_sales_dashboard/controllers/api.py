# -*- coding: utf-8 -*-
"""Public REST-style API stubs for BI Sales."""

from odoo import http
from odoo.http import request


class RnBiApiController(http.Controller):
    """API for KPIs, charts, forecast, and targets."""

    @http.route('/api/rn_bi_sales/v1/kpis', type='json', auth='user')
    def api_kpis(self, filters=None, **kwargs):
        data = request.env['rn.bi.dashboard.service'].get_dashboard_data(filters or {})
        return {'ok': True, 'cards': data.get('cards')}

    @http.route('/api/rn_bi_sales/v1/charts', type='json', auth='user')
    def api_charts(self, filters=None, **kwargs):
        data = request.env['rn.bi.dashboard.service'].get_dashboard_data(filters or {})
        return {'ok': True, 'charts': data.get('charts')}

    @http.route('/api/rn_bi_sales/v1/forecast', type='json', auth='user')
    def api_forecast(self, filters=None, **kwargs):
        data = request.env['rn.bi.dashboard.service'].get_dashboard_data(filters or {})
        return {'ok': True, 'forecast': data.get('forecast')}

    @http.route('/api/rn_bi_sales/v1/targets', type='json', auth='user')
    def api_targets(self, **kwargs):
        return {'ok': True, 'target': request.env['rn.bi.target.service'].get_current_target()}

    @http.route('/rn_bi_sales/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_bi_sales_dashboard'})
