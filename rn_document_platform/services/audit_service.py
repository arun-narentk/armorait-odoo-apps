# -*- coding: utf-8 -*-
"""Audit trail logging."""

import logging

from odoo import models
from odoo.http import request as http_request

_logger = logging.getLogger(__name__)


class RnDocAuditService(models.AbstractModel):
    _name = 'rn.doc.audit.service'
    _description = 'Document Audit Service'

    def log_event(self, sign_request, action, signer=None, comment=None):
        ip_addr = False
        user_agent = False
        try:
            if http_request and http_request.httprequest:
                ip_addr = http_request.httprequest.remote_addr
                user_agent = (http_request.httprequest.user_agent.string or '')[:255]
        except Exception:
            pass

        return self.env['rn.doc.sign.audit'].create({
            'request_id': sign_request.id,
            'signer_id': signer.id if signer else False,
            'user_id': self.env.user.id,
            'action': action,
            'ip_address': ip_addr,
            'user_agent': user_agent,
            'document_hash': sign_request.document_hash,
            'comment': comment,
        })
