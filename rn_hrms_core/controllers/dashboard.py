# -*- coding: utf-8 -*-
"""JSON endpoint for OWL HR dashboard."""

from odoo import http
from odoo.http import request


class RnHrmsDashboardController(http.Controller):
    """Serve dashboard payload."""

    @http.route('/rn_hrms_core/data', type='json', auth='user')
    def dashboard_data(self, company_id=None, **kwargs):
        return request.env['rn.hrms.dashboard.service'].get_dashboard_data(company_id)
