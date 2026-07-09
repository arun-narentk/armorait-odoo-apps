# -*- coding: utf-8 -*-
"""JSON endpoint for OWL dashboard."""

from odoo import http
from odoo.http import request


class RnBookingDashboardController(http.Controller):
    """Serve dashboard payload."""

    @http.route('/rn_booking_platform/data', type='json', auth='user')
    def dashboard_data(self, company_id=None, **kwargs):
        return request.env['rn.booking.dashboard.service'].get_dashboard_data(company_id)
