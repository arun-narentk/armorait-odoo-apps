# -*- coding: utf-8 -*-
"""Health endpoint for CRM Ultimate Pro."""

from odoo import http
from odoo.http import request


class RnCrmPortalController(http.Controller):
    """Public health check."""

    @http.route('/rn_crm/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_crm_ultimate_pro'})
