# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class RnFieldDiffController(http.Controller):

    @http.route('/rn_field_diff/diffs', type='json', auth='user')
    def get_field_diffs(self, model, res_id, limit=50):
        if not model or not res_id:
            return []
        return request.env['rn.field.diff.service'].get_diffs_for_web(model, res_id, limit=limit)

    @http.route('/rn_field_diff/summary', type='json', auth='user')
    def get_field_diff_summary(self, model, res_id):
        if not model or not res_id:
            return {}
        return request.env['rn.field.diff.service'].get_summary(model, res_id)
