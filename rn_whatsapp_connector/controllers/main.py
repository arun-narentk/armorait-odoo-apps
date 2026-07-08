# -*- coding: utf-8 -*-
"""Public HTTP controllers."""

from odoo import http
from odoo.http import request


class RnWhatsappMainController(http.Controller):
    """Health and utility routes for WhatsApp Connector."""

    @http.route('/rn_whatsapp/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        """Return a simple health check for monitoring."""
        return request.make_json_response({'status': 'ok', 'module': 'rn_whatsapp_connector'})
