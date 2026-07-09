# -*- coding: utf-8 -*-
"""Backend JSON endpoint for OWL shell."""

from odoo import http
from odoo.http import request


class RnDashboardController(http.Controller):

    @http.route('/rn_dashboard_core/data', type='json', auth='user')
    def dashboard_data(self, dashboard_id=None, filter_vals=None):
        return request.env['rn.dashboard.service'].get_dashboard_data(
            dashboard_id=dashboard_id,
            filter_vals=filter_vals or {},
        )
