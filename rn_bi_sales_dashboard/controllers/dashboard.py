# -*- coding: utf-8 -*-
"""JSON endpoints used by the OWL dashboard client action."""

from odoo import http
from odoo.http import request


class RnBiDashboardController(http.Controller):
    """Serve dashboard payload to the frontend."""

    @http.route('/rn_bi_sales/data', type='json', auth='user')
    def dashboard_data(self, filters=None, **kwargs):
        return request.env['rn.bi.dashboard.service'].get_dashboard_data(filters or {})
