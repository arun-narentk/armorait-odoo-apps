# -*- coding: utf-8 -*-
"""Multilingual translation hooks (Phase 1 stub)."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)

LANG_LABEL = {
    'ta': '[Tamil draft placeholder]',
    'hi': '[Hindi draft placeholder]',
    'fr': '[French draft placeholder]',
    'de': '[German draft placeholder]',
    'ar': '[Arabic draft placeholder]',
    'es': '[Spanish draft placeholder]',
}


class RnAiEmailTranslationService(models.AbstractModel):
    _name = 'rn.ai.email.translation.service'
    _description = 'AI Email Translation Service'

    def translate_stub(self, body, language):
        label = LANG_LABEL.get(language)
        if not label:
            return body
        return f'{label}\n\n{body}'
