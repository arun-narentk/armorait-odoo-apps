# -*- coding: utf-8 -*-
"""Service layer for natural-language domain parsing."""

from __future__ import annotations

import ast
import json
from datetime import date

from odoo import _, api, models
from odoo.exceptions import UserError

from ..constants import SUGGESTION_CHIPS, SUPPORTED_MODELS
from .domain_engine import DictionaryEntry, parse_description


class RnDomainParserService(models.AbstractModel):
    _name = 'rn.domain.parser.service'
    _description = 'Domain Parser Service'

    @api.model
    def supported_models(self):
        installed = []
        for model_name, label in SUPPORTED_MODELS:
            if model_name in self.env:
                installed.append({'model': model_name, 'label': label})
        return installed

    @api.model
    def _dictionary_entries(self, res_model: str) -> list[DictionaryEntry]:
        Dictionary = self.env['rn.domain.dictionary']
        rows = Dictionary.search([
            ('res_model', '=', res_model),
            ('active', '=', True),
        ], order='sequence, trigger_word')
        entries = []
        for row in rows:
            entries.append(DictionaryEntry(
                trigger=row.trigger_word.lower(),
                field_name=row.field_name,
                operator=row.operator,
                value=row.get_resolved_value(),
                value_type=row.value_type,
            ))
        return entries

    @api.model
    def parse(self, res_model: str, description: str) -> dict:
        if res_model not in self.env:
            raise UserError(_('Unsupported model: %s') % res_model)
        self.env[res_model].check_access('read')
        entries = self._dictionary_entries(res_model)
        if not entries:
            raise UserError(_('No dictionary entries configured for %s.') % res_model)
        result = parse_description(
            description,
            entries,
            suggestion_pool=SUGGESTION_CHIPS,
            today=date.today(),
        )
        domain_text = self._format_domain(result.domain)
        validator = self.env['rn.domain.validator.service']
        validation = validator.validate(res_model, result.domain)
        record_count = 0
        if validation['valid'] and result.domain:
            record_count = self.env[res_model].search_count(result.domain)
        return {
            'domain': result.domain,
            'domain_text': domain_text,
            'record_count': record_count,
            'suggestions': result.suggestions,
            'warnings': result.warnings + validation.get('errors', []),
            'valid': validation['valid'],
        }

    @api.model
    def _format_domain(self, domain: list) -> str:
        if not domain:
            return '[]'
        return json.dumps(domain, indent=2)

    @api.model
    def load_domain_text(self, domain_text: str) -> list:
        try:
            parsed = ast.literal_eval(domain_text.strip() or '[]')
        except (SyntaxError, ValueError) as exc:
            raise UserError(_('Invalid domain syntax: %s') % exc) from exc
        if not isinstance(parsed, list):
            raise UserError(_('Domain must be a list.'))
        return parsed

    @api.model
    def suggest_for_partial(self, res_model: str, partial: str) -> list[str]:
        entries = self._dictionary_entries(res_model)
        lowered = (partial or '').lower()
        chips = {entry.trigger for entry in entries}
        chips.update(SUGGESTION_CHIPS)
        return sorted(chip for chip in chips if not lowered or chip.startswith(lowered))[:12]
