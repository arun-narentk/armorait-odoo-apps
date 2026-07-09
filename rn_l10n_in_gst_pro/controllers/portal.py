# -*- coding: utf-8 -*-
"""Portal placeholders for future taxpayer portal views."""

from odoo import http
from odoo.http import request


class RnGstPortalController(http.Controller):
    """Public health check while portal pages are deferred."""

    @http.route('/rn_gst/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_l10n_in_gst_pro'})
