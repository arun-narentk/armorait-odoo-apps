# -*- coding: utf-8 -*-
"""Business logic for configurable name generation."""

from __future__ import annotations

import logging
from typing import Any

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.rn_name_assistant import constants
from odoo.addons.rn_name_assistant.services.name_utils import (
    apply_template,
    cleanup_name,
    normalize_key,
    score_name,
)

_logger = logging.getLogger(__name__)


class RnNameGeneratorService(models.AbstractModel):
    _name = 'rn.name.generator.service'
    _description = 'Name Generator Service'

    @api.model
    def _abbreviation_map(self):
        rows = self.env['rn.name.abbreviation'].sudo().search([('active', '=', True)])
        return {row.short_form: row.expansion for row in rows}

    @api.model
    def _get_target_record(self, res_model: str, res_id: int):
        if res_model not in self.env:
            raise UserError(_('Unsupported model: %s') % res_model)
        record = self.env[res_model].browse(res_id)
        if not record.exists():
            raise UserError(_('Record not found.'))
        record.check_access('read')
        return record

    @api.model
    def _current_name(self, record) -> str:
        if 'name' in record._fields:
            return (record.name or '').strip()
        return ''

    @api.model
    def _field_values(self, record) -> dict[str, str]:
        values: dict[str, str] = {}
        if 'name' in record._fields:
            values['name'] = (record.name or '').strip()

        for field_name in constants.PRODUCT_NAMING_FIELDS:
            if field_name in record._fields:
                raw = record[field_name]
                values[normalize_key(field_name.replace('rn_', ''))] = (raw or '').strip()

        if record._name == 'product.template' and record.categ_id:
            values['category'] = (record.categ_id.name or '').strip()

        alias_values = {}
        for placeholder, source in constants.PLACEHOLDER_ALIASES.items():
            if source == 'category':
                alias_values[placeholder] = values.get('category', '')
            elif source.startswith('rn_') and source.replace('rn_', '') in values:
                alias_values[placeholder] = values.get(source.replace('rn_', ''), '')
            elif source in values:
                alias_values[placeholder] = values.get(source, '')
        values.update(alias_values)
        return {k: v for k, v in values.items() if v}

    @api.model
    def _generate_name(self, record, template_body: str) -> str:
        values = self._field_values(record)
        rendered = apply_template(template_body, values)
        return cleanup_name(rendered, self._abbreviation_map())

    @api.model
    def _cleanup(self, text: str) -> str:
        return cleanup_name(text or '', self._abbreviation_map())

    @api.model
    def _score_name(self, name: str, record, field_count: int = 0) -> float:
        seed = self._current_name(record)
        return score_name(name, seed=seed, field_count=field_count)

    @api.model
    def _template_matches(self, template, record) -> bool:
        if not template.active:
            return False
        if template.model_name and template.model_name != record._name:
            return False
        if template.condition_domain and template.condition_domain not in ('[]', False):
            try:
                domain = safe_eval(template.condition_domain)
                return bool(record.filtered_domain(domain))
            except (ValueError, SyntaxError) as exc:
                _logger.warning('Invalid template domain on %s: %s', template.display_name, exc)
                return False
        return True

    @api.model
    def _heuristic_variants(self, record) -> list[str]:
        seed = self._current_name(record) or 'Record'
        seed = self._cleanup(seed)
        variants = []

        if record._name == 'res.partner':
            for suffix in constants.CONTACT_SUFFIXES:
                variants.append(f'{seed} {suffix}')
        elif record._name == 'crm.lead':
            for suffix in constants.LEAD_SUFFIXES:
                variants.append(f'{seed} {suffix}')
        elif record._name == 'project.project':
            variants = [
                f'Corporate {seed} Redesign',
                'Customer Portal Development',
                f'{seed} Migration Project',
                f'{seed} Enhancement Initiative',
            ]
        elif record._name == 'project.task':
            for suffix in constants.TASK_SUFFIXES:
                variants.append(f'{seed} {suffix}')
        else:
            values = self._field_values(record)
            if values.get('brand') and values.get('category'):
                variants.append(f"{values['brand']} {values.get('series', '')} {values.get('model', '')}".strip())
        return [self._cleanup(v) for v in variants if v]

    @api.model
    def _synonym_variants(self, base_name: str, category: str = '') -> list[str]:
        variants = []
        cat = (category or '').strip().lower()
        synonyms = constants.CATEGORY_SYNONYMS.get(cat, ())
        for synonym in synonyms:
            variants.append(base_name.replace(category, synonym.title(), 1))
        return [self._cleanup(v) for v in variants if v and v != base_name]

    @api.model
    def _generate_variants(self, record, max_count: int | None = None) -> list[dict[str, Any]]:
        max_count = max_count or constants.DEFAULT_MAX_SUGGESTIONS
        suggestions: list[dict[str, Any]] = []
        seen: set[str] = set()
        values = self._field_values(record)

        templates = self.env['rn.name.template'].search(
            [
                ('active', '=', True),
                '|',
                ('model_name', '=', record._name),
                ('model_name', '=', False),
            ],
            order='priority desc, sequence, id',
        )

        for template in templates:
            if not self._template_matches(template, record):
                continue
            name = self._generate_name(record, template.template_body)
            if name and name.lower() not in seen:
                seen.add(name.lower())
                suggestions.append({
                    'name': name,
                    'score': self._score_name(name, record, len(values)),
                    'template_id': template.id,
                })
            for alt_body in template.variant_template_ids.mapped('template_body'):
                alt_name = self._generate_name(record, alt_body)
                if alt_name and alt_name.lower() not in seen:
                    seen.add(alt_name.lower())
                    suggestions.append({
                        'name': alt_name,
                        'score': self._score_name(alt_name, record, len(values)),
                        'template_id': template.id,
                    })
            category = values.get('category', '')
            for synonym_name in self._synonym_variants(name, category):
                if synonym_name.lower() not in seen:
                    seen.add(synonym_name.lower())
                    suggestions.append({
                        'name': synonym_name,
                        'score': self._score_name(synonym_name, record, len(values)),
                        'template_id': template.id,
                    })

        for variant in self._heuristic_variants(record):
            if variant.lower() not in seen:
                seen.add(variant.lower())
                suggestions.append({
                    'name': variant,
                    'score': self._score_name(variant, record, 1),
                    'template_id': False,
                })

        suggestions.sort(key=lambda row: row['score'], reverse=True)
        return suggestions[:max_count]

    @api.model
    def preview_name(self, res_model: str, values: dict, template_body: str) -> str:
        normalized = {normalize_key(k): (v or '').strip() for k, v in values.items() if v}
        rendered = apply_template(template_body, normalized)
        return cleanup_name(rendered, self._abbreviation_map())

    @api.model
    def generate_for_record(self, res_model: str, res_id: int, max_count: int | None = None):
        record = self._get_target_record(res_model, res_id)
        return self._generate_variants(record, max_count=max_count)

    @api.model
    def apply_selected_name(self, res_model: str, res_id: int, new_name: str):
        record = self._get_target_record(res_model, res_id)
        record.check_access('write')
        cleaned = self._cleanup(new_name)
        if not cleaned:
            raise UserError(_('Suggested name is empty.'))
        if 'name' not in record._fields:
            raise UserError(_('This record has no name field.'))
        record.write({'name': cleaned})
        return cleaned

    @api.model
    def batch_generate(self, res_model: str, res_ids: list[int], max_count: int = 1):
        results = []
        for res_id in res_ids:
            try:
                record = self._get_target_record(res_model, res_id)
                current = self._current_name(record)
                suggestions = self._generate_variants(record, max_count=max_count)
                top = suggestions[0]['name'] if suggestions else ''
                results.append({
                    'res_id': res_id,
                    'current_name': current,
                    'suggested_name': top,
                    'all_suggestions': '; '.join(row['name'] for row in suggestions),
                })
            except UserError as exc:
                results.append({
                    'res_id': res_id,
                    'current_name': '',
                    'suggested_name': '',
                    'all_suggestions': str(exc),
                })
        return results
