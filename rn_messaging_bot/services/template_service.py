# -*- coding: utf-8 -*-
"""Template rendering for outbound messaging."""

from __future__ import annotations

import re

from odoo import api, models

_PLACEHOLDER_RE = re.compile(r'\{\{\s*([a-zA-Z0-9_]+)\s*\}\}')


class RnMessagingTemplateService(models.AbstractModel):
    _name = 'rn.messaging.template.service'
    _description = 'Messaging Template Service'

    @api.model
    def render(self, template, partner=None, conversation=None, extra_values=None):
        values = self._build_values(partner, conversation, extra_values or {})
        body = template.body or ''
        return _PLACEHOLDER_RE.sub(
            lambda match: values.get(match.group(1), match.group(0)),
            body,
        )

    @api.model
    def _build_values(self, partner, conversation, extra_values):
        company = self.env.company
        if conversation:
            company = conversation.company_id or company
        partner = partner or (conversation.partner_id if conversation else self.env['res.partner'])
        values = {
            'partner_name': partner.name or '',
            'name': partner.name or '',
            'phone': partner.phone or '',
            'email': partner.email or '',
            'company': company.name or '',
            'conversation': conversation.name if conversation else '',
        }
        values.update(extra_values)
        return values
