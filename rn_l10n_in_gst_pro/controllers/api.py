# -*- coding: utf-8 -*-
"""REST API stubs for GST Pro."""

from odoo import http
from odoo.http import request


class RnGstApiController(http.Controller):
    """JSON API placeholders expanded in later phases."""

    @http.route('/api/rn_gst/v1/summary', type='json', auth='user')
    def api_summary(self, **kwargs):
        return request.env['rn.gst.dashboard.service'].get_kpis()

    @http.route('/api/rn_gst/v1/returns', type='json', auth='user')
    def api_returns(self, **kwargs):
        returns = request.env['rn.gst.return'].search([], limit=50)
        return {
            'ok': True,
            'returns': [{
                'id': r.id,
                'name': r.name,
                'return_type': r.return_type,
                'state': r.state,
            } for r in returns],
        }

    @http.route('/api/rn_gst/v1/validate', type='json', auth='user')
    def api_validate(self, return_id=None, **kwargs):
        if not return_id:
            return {'ok': False, 'error': 'return_id required'}
        gst_return = request.env['rn.gst.return'].browse(int(return_id)).exists()
        if not gst_return:
            return {'ok': False, 'error': 'Return not found'}
        request.env['rn.gst.validation.service'].validate_returns(gst_return)
        return {'ok': True, 'error_count': gst_return.error_count}
