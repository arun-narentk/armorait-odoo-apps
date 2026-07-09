# -*- coding: utf-8 -*-
"""Core signing workflow orchestration."""

import hashlib
import logging
import secrets
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnDocSignService(models.AbstractModel):
    _name = 'rn.doc.sign.service'
    _description = 'Document Sign Service'

    def send_request(self, request):
        request.ensure_one()
        settings = self._get_settings(request.company_id.id)
        if settings.signature_credit_balance <= 0:
            raise UserError('Signature credit balance is zero. Add credits to continue.')

        doc_hash = self._hash_attachment(request.attachment_id)
        request.write({
            'state': 'sent',
            'document_hash': doc_hash,
        })
        settings.signature_credit_balance -= 1

        request.signer_ids.write({'is_active': False})
        if request.sign_mode == 'sequential':
            first = request.signer_ids.sorted('sequence')[:1]
            first.write({'is_active': True, 'state': 'sent', 'access_token': secrets.token_urlsafe(24)})
            self.env['rn.doc.invitation.service'].send_invitation(request, first)
        else:
            for signer in request.signer_ids:
                signer.write({
                    'is_active': True,
                    'state': 'sent',
                    'access_token': secrets.token_urlsafe(24),
                })
                self.env['rn.doc.invitation.service'].send_invitation(request, signer)

        self.env['rn.doc.audit.service'].log_event(request, 'send')
        return request

    def complete_signer(self, signer):
        signer.ensure_one()
        signer.write({
            'state': 'signed',
            'signed_on': fields.Datetime.now(),
        })
        self.env['rn.doc.audit.service'].log_event(
            signer.request_id, 'sign', signer=signer,
        )
        request = signer.request_id
        pending = request.signer_ids.filtered(lambda s: s.state not in ('signed', 'declined'))

        if request.sign_mode == 'sequential':
            next_signer = request.signer_ids.filtered(
                lambda s: s.state == 'pending'
            ).sorted('sequence')[:1]
            if next_signer:
                request.write({'state': 'partial'})
                next_signer.write({
                    'is_active': True,
                    'state': 'sent',
                    'access_token': secrets.token_urlsafe(24),
                })
                self.env['rn.doc.invitation.service'].send_invitation(request, next_signer)
            elif not pending:
                self._complete_request(request)
        elif not pending:
            self._complete_request(request)
        else:
            request.write({'state': 'partial'})
        return signer

    def _complete_request(self, request):
        request.write({'state': 'completed'})
        self.env['rn.doc.audit.service'].log_event(request, 'complete')
        if request.res_model and request.res_id:
            doc = self.env[request.res_model].browse(request.res_id)
            if doc.exists() and hasattr(doc, 'message_post'):
                doc.message_post(body=f'Document {request.reference} fully signed.')

    def _hash_attachment(self, attachment):
        if not attachment or not attachment.datas:
            return False
        raw = attachment.datas
        if isinstance(raw, str):
            import base64
            raw = base64.b64decode(raw)
        return hashlib.sha256(raw).hexdigest()

    def _get_settings(self, company_id):
        settings = self.env['rn.doc.platform.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        if not settings:
            settings = self.env['rn.doc.platform.settings'].create({'company_id': company_id})
        return settings
