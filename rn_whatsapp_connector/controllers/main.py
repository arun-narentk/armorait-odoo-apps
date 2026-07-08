# -*- coding: utf-8 -*-
"""Backend helpers for WhatsApp connector."""

from odoo import http
from odoo.http import request


class RnWhatsappMainController(http.Controller):

    @http.route('/rn_whatsapp/dashboard/data', type='json', auth='user')
    def dashboard_data(self):
        return request.env['rn.whatsapp.dashboard.service'].get_dashboard_data()
