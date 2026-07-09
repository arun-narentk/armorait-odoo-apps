# -*- coding: utf-8 -*-
"""DOCX export stub for later python-docx phase."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiDocumentDocxService(models.AbstractModel):
    _name = 'rn.ai.document.docx.service'
    _description = 'AI Document DOCX Service'

    def export_docx(self, document):
        document.ensure_one()
        _logger.info('DOCX export placeholder for %s (install python-docx in later phase)', document.name)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'DOCX Export',
                'message': 'DOCX export lands in a follow-up phase. Use PDF print for now.',
                'type': 'info',
                'sticky': False,
            },
        }
