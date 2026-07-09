# -*- coding: utf-8 -*-
"""Template rendering helpers."""

import json
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWhatsappTemplateService(models.AbstractModel):
    _name = 'rn.whatsapp.template.service'
    _description = 'WhatsApp Template Service'

    def parse_vars_json(self, raw):
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except (TypeError, ValueError):
            return {}

    def render(self, template, values=None):
        values = values or {}
        body = template.body or ''
        for key, value in values.items():
            body = body.replace('{{%s}}' % key, str(value))
            body = body.replace('{{ %s }}' % key, str(value))
        return body

    def extract_record_vars(self, record, variable_names):
        values = {}
        for name in (variable_names or []):
            name = (name or '').strip()
            if not name:
                continue
            try:
                values[name] = record.mapped(name)[0] if '.' in name else (getattr(record, name, '') or '')
            except Exception:  # noqa: BLE001
                values[name] = ''
            if hasattr(values[name], 'name'):
                values[name] = values[name].name
            values[name] = str(values[name] or '')
        # Common convenience keys
        if 'name' not in values and hasattr(record, 'name'):
            values['name'] = record.name or ''
        if 'partner' not in values and hasattr(record, 'partner_id') and record.partner_id:
            values['partner'] = record.partner_id.name
        return values
