# -*- coding: utf-8 -*-
"""Built-in signature tracking; external e-sign via future connectors."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiDocumentSignatureService(models.AbstractModel):
    _name = 'rn.ai.document.signature.service'
    _description = 'AI Document Signature Service'

    def mark_signed(self, documents):
        for document in documents:
            document.write({
                'state': 'signed',
                'signed_date': fields.Datetime.now(),
            })
            self.env['rn.ai.document.version.service'].snapshot(document, reason='Signed')
            _logger.info('Marked document %s as signed (built-in)', document.name)
        return True
