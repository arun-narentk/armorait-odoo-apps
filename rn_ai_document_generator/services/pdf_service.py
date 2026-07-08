# -*- coding: utf-8 -*-
"""PDF helpers (report action wrapper for Phase 1)."""

from odoo import models


class RnAiDocumentPdfService(models.AbstractModel):
    _name = 'rn.ai.document.pdf.service'
    _description = 'AI Document PDF Service'

    def print_documents(self, documents):
        return self.env.ref('rn_ai_document_generator.action_report_rn_ai_document').report_action(documents)
