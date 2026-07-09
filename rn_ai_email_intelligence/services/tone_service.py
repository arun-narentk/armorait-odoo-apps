# -*- coding: utf-8 -*-
"""Apply tone adjustments to draft text."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)

TONE_PREFIX = {
    'friendly': 'Hope you are having a great day. ',
    'formal': 'Dear Sir/Madam, ',
    'executive': 'At the executive level, we would like to note that ',
    'apologetic': 'We sincerely apologize for any inconvenience. ',
    'concise': '',
    'persuasive': 'We believe this offer provides strong value for your business. ',
    'followup': 'Following up on our previous message, ',
}


class RnAiEmailToneService(models.AbstractModel):
    _name = 'rn.ai.email.tone.service'
    _description = 'AI Email Tone Service'

    def apply_tone(self, body, tone):
        prefix = TONE_PREFIX.get(tone, '')
        if prefix and not body.startswith(prefix):
            return prefix + body
        return body
