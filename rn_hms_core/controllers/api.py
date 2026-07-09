# -*- coding: utf-8 -*-
"""REST-style API stubs for HMS core."""

from odoo import http
from odoo.http import request


class RnHmsApiController(http.Controller):
    """API for dashboard and patients."""

    @http.route('/api/rn_hms/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return {'ok': True, 'data': request.env['rn.hms.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_hms/v1/patients', type='json', auth='user')
    def api_patients(self, **kwargs):
        patients = request.env['rn.hms.patient'].search_read(
            [('company_id', '=', request.env.company.id)],
            ['name', 'patient_code', 'phone', 'email', 'blood_group'],
            limit=200,
        )
        return {'ok': True, 'patients': patients}

    @http.route('/rn_hms_core/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_hms_core'})
