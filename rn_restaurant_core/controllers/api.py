# -*- coding: utf-8 -*-
"""Health and authenticated API stubs."""

from odoo import http
from odoo.http import request


class RnRestaurantApiController(http.Controller):

    @http.route('/rn_restaurant_core/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'ok': True, 'module': 'rn_restaurant_core'})

    @http.route('/api/rn_restaurant/v1/dashboard', type='json', auth='user')
    def api_dashboard(self):
        return {'ok': True, 'data': request.env['rn.restaurant.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_restaurant/v1/menu', type='json', auth='user')
    def api_menu(self, restaurant_id, channel='dine_in'):
        restaurant = request.env['rn.restaurant'].browse(restaurant_id)
        items = request.env['rn.restaurant.menu.service'].available_items(restaurant, channel=channel)
        return {
            'ok': True,
            'data': [{
                'id': i.id,
                'name': i.name,
                'price': i.list_price,
                'category': i.category_id.name,
                'station': i.kitchen_station,
            } for i in items],
        }
