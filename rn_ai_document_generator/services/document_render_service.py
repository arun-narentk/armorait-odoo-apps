# -*- coding: utf-8 -*-
"""Orchestrate placeholder fill + AI clauses + version snapshot."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiDocumentRenderService(models.AbstractModel):
    _name = 'rn.ai.document.render.service'
    _description = 'AI Document Render Service'

    def generate_documents(self, documents):
        Placeholder = self.env['rn.ai.document.placeholder.service']
        AI = self.env['rn.ai.document.ai.generation.service']
        Version = self.env['rn.ai.document.version.service']
        for document in documents:
            template = document.template_id
            prepared = self.env['rn.ai.document.template.service'].prepare_body(
                template,
                style=document.style,
                language=document.language,
            )
            values = Placeholder.build_context(document)
            ai_result = AI.generate_sections(document, values)
            body = AI.inject_sections(prepared['body_html'], ai_result.get('sections'))
            body = Placeholder.render(body, values)
            document.write({
                'body_html': body,
                'placeholder_values': Placeholder.dump_values(values),
                'ai_notes': ai_result.get('notes'),
                'state': 'generated',
                'style': prepared['style'],
                'language': prepared['language'],
            })
            Version.snapshot(document, reason='AI generate')
            _logger.info('Generated AI document %s', document.name)
        return True
