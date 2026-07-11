# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class FilterManagerController(http.Controller):

    @http.route('/rn/filter/health', type='http', auth='public', methods=['GET'], csrf=False)
    def rn_filter_health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_filter_manager'})

    @http.route('/rn/filter/suggestions', type='http', auth='user', methods=['GET'], csrf=False)
    def rn_filter_suggestions(self):
        suggestions = request.env['rn.filter.service'].suggest_pin()
        return request.make_json_response({'suggestions': suggestions})
