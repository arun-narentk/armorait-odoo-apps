# -*- coding: utf-8 -*-
"""JSON endpoint for OWL dashboard."""

from odoo import http
from odoo.http import request


class RnInvForecastDashboardController(http.Controller):
    """Serve dashboard payload."""

    @http.route('/rn_inventory_forecast/data', type='json', auth='user')
    def dashboard_data(self, company_id=None, **kwargs):
        return request.env['rn.inv.dashboard.service'].get_dashboard_data(company_id)
