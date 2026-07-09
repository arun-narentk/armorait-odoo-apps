# -*- coding: utf-8 -*-
"""Public signing portal routes."""

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnDocPortalController(http.Controller):

    @http.route('/sign/document/<string:token>', type='http', auth='public', website=True)
    def sign_document(self, token, **kwargs):
        signer = request.env['rn.doc.sign.signer'].sudo().search([
            ('access_token', '=', token),
            ('state', 'in', ('sent', 'pending')),
        ], limit=1)
        if not signer:
            return request.render('rn_document_platform.portal_sign_invalid', {})
        req = signer.request_id
        request.env['rn.doc.audit.service'].sudo().log_event(req, 'view', signer=signer)
        return request.render('rn_document_platform.portal_sign_document', {
            'signer': signer,
            'sign_request': req,
        })

    @http.route('/sign/document/<string:token>/accept', type='http', auth='public', methods=['POST'], website=True)
    def accept_signature(self, token, **post):
        signer = request.env['rn.doc.sign.signer'].sudo().search([
            ('access_token', '=', token),
        ], limit=1)
        if not signer:
            return request.redirect('/sign/document/%s' % token)
        if post.get('signature_data'):
            signer.write({'signature_image': post.get('signature_data')})
        request.env['rn.doc.sign.service'].sudo().complete_signer(signer)
        return request.render('rn_document_platform.portal_sign_thanks', {
            'signer': signer,
            'sign_request': signer.request_id,
        })
