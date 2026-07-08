# -*- coding: utf-8 -*-
"""Template helpers."""

from odoo import models


class RnAiDocumentTemplateService(models.AbstractModel):
    _name = 'rn.ai.document.template.service'
    _description = 'AI Document Template Service'

    def prepare_body(self, template, style=None, language=None):
        template.ensure_one()
        body = template.body_html or '<p></p>'
        return {
            'body_html': body,
            'style': style or template.style,
            'language': language or template.language,
            'ai_prompt': template.ai_prompt or '',
            'type_id': template.type_id,
        }
