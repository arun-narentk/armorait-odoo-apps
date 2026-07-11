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
