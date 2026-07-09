# -*- coding: utf-8 -*-
"""REST-style API stubs for rental core."""

from odoo import http
from odoo.http import request


class RnRentalApiController(http.Controller):
    """API for dashboard, availability, and assets."""

    @http.route('/api/rn_rental/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return {'ok': True, 'data': request.env['rn.rental.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_rental/v1/availability', type='json', auth='user')
    def api_availability(self, asset_id=None, date_start=None, date_end=None, **kwargs):
        asset = request.env['rn.rental.asset'].browse(asset_id)
        if not asset.exists():
            return {'ok': False, 'error': 'Asset not found'}
        available = request.env['rn.rental.availability.service'].is_available(
            asset, date_start, date_end
        )
        return {'ok': True, 'available': available}

    @http.route('/rn_rental_core/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_rental_core'})
