# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class UniversalQrController(http.Controller):

    @http.route('/rn/qr/health', type='http', auth='public', methods=['GET'], csrf=False)
    def rn_qr_health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_universal_qr'})

    @http.route('/rn/qr/<string:token>', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def rn_qr_scan(self, token, **kwargs):
        result = request.env['rn.qr.scan.service'].sudo().resolve_token(token)
        if not result:
            return request.not_found()
        qr_record, document = result
        request.env['rn.qr.scan.service'].sudo().log_scan(
            qr_record=qr_record,
            source='web',
            user_agent=request.httprequest.headers.get('User-Agent'),
            ip_address=request.httprequest.remote_addr,
        )
        return request.redirect(f'/web#id={document.id}&model={document._name}&view_type=form')

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class UniversalQrController(http.Controller):

    @http.route('/rn/qr/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self, **kwargs):
        return request.make_json_response({'status': 'ok', 'module': 'rn_universal_qr'})

    @http.route('/rn/qr/<string:token>', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def scan(self, token, **kwargs):
        result = request.env['rn.qr.scan.service'].sudo().resolve_token(token)
        if not result:
            return request.not_found()
        qr_record, document = result
        request.env['rn.qr.scan.service'].sudo().log_scan(
            qr_record=qr_record,
            source='web',
            user_agent=request.httprequest.headers.get('User-Agent'),
            ip_address=request.httprequest.remote_addr,
        )
        return request.redirect(f'/web#id={document.id}&model={document._name}&view_type=form')
# -*- coding: utf-8 -*-
"""Public QR scan route and health check."""

import logging

from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnUniversalQrController(http.Controller):

    @http.route('/rn/qr/<string:token>', type='http', auth='public', website=False, csrf=False, sitemap=False)
    def scan_qr(self, token, **kwargs):
        user_agent = request.httprequest.headers.get('User-Agent')
        ip_address = request.httprequest.remote_addr
        user = request.env.user
        try:
            result = request.env['rn.qr.scan.service'].sudo().process_token(
                token,
                user_agent=user_agent,
                ip_address=ip_address,
                user=user,
            )
        except UserError as exc:
            return request.make_response(
                '<html><body><h1>QR Error</h1><p>%s</p></body></html>' % exc.args[0],
                headers=[('Content-Type', 'text/html')],
                status=404,
            )

        if result.get('type') == 'redirect':
            return request.redirect(result['url'], code=302)
        return request.redirect('/web', code=302)

    @http.route('/rn/qr/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_universal_qr'})
