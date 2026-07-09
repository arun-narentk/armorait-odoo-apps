# -*- coding: utf-8 -*-
"""JSON endpoint for OWL hospital dashboard."""

from odoo import http
from odoo.http import request


class RnHmsDashboardController(http.Controller):
    """Serve dashboard payload."""

    @http.route('/rn_hms_core/data', type='json', auth='user')
    def dashboard_data(self, company_id=None, **kwargs):
        return request.env['rn.hms.dashboard.service'].get_dashboard_data(company_id)
