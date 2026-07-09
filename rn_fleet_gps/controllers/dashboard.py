# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class RnFleetDashboardController(http.Controller):

    @http.route('/rn_fleet_gps/data', type='json', auth='user')
    def dashboard_data(self, vehicle_id=None):
        return request.env['rn.fleet.dashboard.service'].get_dashboard_data(vehicle_id=vehicle_id)
