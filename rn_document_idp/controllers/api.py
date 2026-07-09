# -*- coding: utf-8 -*-
"""REST API for document capture."""

import base64
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnDocumentIdpApiController(http.Controller):

    @http.route('/rn_document_idp/api/capture', type='http', auth='user', methods=['POST'], csrf=False)
    def capture_document(self, **kwargs):
        """Accept JSON or multipart upload for document capture."""
        try:
            payload = request.get_json_data() or {}
        except Exception:
            payload = {}
        name = payload.get('name') or kwargs.get('name') or 'API Capture'
        channel = payload.get('capture_channel') or 'api'
        attachment = False
        if payload.get('file_base64'):
            attachment = request.env['ir.attachment'].sudo().create({
                'name': payload.get('filename') or f'{name}.pdf',
                'datas': payload.get('file_base64'),
                'mimetype': payload.get('mimetype') or 'application/pdf',
            })
        if not attachment:
            return request.make_json_response({'error': 'file_base64 is required'}, status=400)
        document = request.env['rn.document.idp.document'].create({
            'name': name,
            'attachment_id': attachment.id,
            'capture_channel': channel,
        })
        if payload.get('auto_process', True):
            document.action_process()
        return request.make_json_response({
            'id': document.id,
            'reference': document.reference,
            'state': document.state,
            'document_type': document.document_type,
        })

    @http.route('/rn_document_idp/api/search', type='json', auth='user', methods=['POST'])
    def search_documents(self, query, limit=20):
        return request.env['rn.document.idp.search.service'].search_documents(query, limit=limit)
