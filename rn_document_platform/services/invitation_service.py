# -*- coding: utf-8 -*-
"""Email invitations to signers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnDocInvitationService(models.AbstractModel):
    _name = 'rn.doc.invitation.service'
    _description = 'Document Invitation Service'

    def send_invitation(self, sign_request, signer):
        settings = self.env['rn.doc.platform.settings'].search(
            [('company_id', '=', sign_request.company_id.id)], limit=1,
        )
        if settings and not settings.enable_email_invite:
            return False
        template = self.env.ref(
            'rn_document_platform.mail_template_sign_invitation',
            raise_if_not_found=False,
        )
        if not template or not signer.email:
            sign_request.message_post(
                body=f'Sign invitation queued for {signer.name} ({signer.email}).',
            )
            return False
        template.with_context(signer_name=signer.name).send_mail(
            sign_request.id,
            force_send=False,
            email_values={'email_to': signer.email},
        )
        self.env['rn.doc.audit.service'].log_event(sign_request, 'remind', signer=signer)
        return True
