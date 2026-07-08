# -*- coding: utf-8 -*-
"""Backend JSON for OWL overview."""

from odoo import http
from odoo.http import request


class RnRestaurantDashboardController(http.Controller):

    @http.route('/rn_restaurant_core/data', type='json', auth='user')
    def dashboard_data(self):
        return request.env['rn.restaurant.dashboard.service'].get_dashboard_data()
