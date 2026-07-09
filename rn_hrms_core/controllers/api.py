# -*- coding: utf-8 -*-
"""REST-style API stubs for HRMS core."""

from odoo import http
from odoo.http import request


class RnHrmsApiController(http.Controller):
    """API for dashboard and employee directory."""

    @http.route('/api/rn_hrms/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return {'ok': True, 'data': request.env['rn.hrms.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_hrms/v1/employees', type='json', auth='user')
    def api_employees(self, **kwargs):
        employees = request.env['hr.employee'].search_read(
            [('company_id', '=', request.env.company.id)],
            ['name', 'rn_hrms_employee_code', 'department_id', 'work_email'],
            limit=200,
        )
        return {'ok': True, 'employees': employees}

    @http.route('/rn_hrms_core/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_hrms_core'})
