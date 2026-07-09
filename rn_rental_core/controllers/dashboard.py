# -*- coding: utf-8 -*-
"""JSON endpoint for OWL rental dashboard."""

from odoo import http
from odoo.http import request


class RnRentalDashboardController(http.Controller):
    """Serve dashboard payload."""

    @http.route('/rn_rental_core/data', type='json', auth='user')
    def dashboard_data(self, company_id=None, **kwargs):
        return request.env['rn.rental.dashboard.service'].get_dashboard_data(company_id)
