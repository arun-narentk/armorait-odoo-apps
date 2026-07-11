# -*- coding: utf-8 -*-
"""Duplicate scan engine."""

from __future__ import annotations

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

from .similarity_service import compare_values, weighted_score

_logger = logging.getLogger(__name__)


class RnDupScanService(models.AbstractModel):
    _name = 'rn.dup.scan.service'
    _description = 'Duplicate Scan Service'

    def run_rule_scan(self, rule):
        rule.ensure_one()
        if rule.model_name not in self.env:
            raise UserError(_('Model %s is not available in this database.') % rule.model_name)
        scan = self.env['rn.dup.scan'].create({
            'name': self.env['ir.sequence'].next_by_code('rn.dup.scan') or _('Duplicate Scan'),
            'rule_id': rule.id,
            'state': 'running',
        })
        try:
            matches, record_count = self._scan_records(rule)
            for match in matches:
                match['scan_id'] = scan.id
            if matches:
                self.env['rn.dup.result'].create(matches)
            scan.write({
                'state': 'done',
                'record_count': record_count,
                'match_count': len(matches),
            })
        except Exception as exc:
            _logger.exception('Duplicate scan failed for rule %s', rule.id)
            scan.write({'state': 'failed', 'error_message': str(exc)})
            raise
        return scan

    def _scan_records(self, rule):
        Model = self.env[rule.model_name]
        domain = rule._get_record_domain()
        records = Model.search(domain, limit=rule.batch_limit, order='id')
        field_lines = rule.field_line_ids.filtered(lambda line: line.field_name in Model._fields)
        if not field_lines:
            raise UserError(_('No valid matching fields found on model %s.') % rule.model_name)

        buckets: dict[str, list] = {}
        for record in records:
            key = self._blocking_key(record, field_lines[0])
            buckets.setdefault(key, []).append(record)

        matches = []
        for bucket in buckets.values():
            if len(bucket) < 2:
                continue
            for idx, left in enumerate(bucket):
                for right in bucket[idx + 1:]:
                    if self.env['rn.dup.ignore'].is_ignored(
                        rule, rule.model_name, left.id, right.id,
                    ):
                        continue
                    score, summary = self._score_pair(left, right, field_lines)
                    if score < rule.match_threshold:
                        continue
                    master_id, duplicate_id = sorted((left.id, right.id))
                    matches.append({
                        'scan_id': False,
                        'model_name': rule.model_name,
                        'res_id': master_id,
                        'duplicate_res_id': duplicate_id,
                        'score': round(score, 2),
                        'match_summary': summary,
                    })
        return matches, len(records)

    def _blocking_key(self, record, first_line):
        value = getattr(record, first_line.field_name, False)
        if first_line.match_type == 'phone':
            from .similarity_service import normalize_phone
            return normalize_phone(value)[:6] or '__empty__'
        from .similarity_service import normalize_text
        text = normalize_text(value)
        return text[:3] if text else '__empty__'

    def _score_pair(self, left, right, field_lines):
        parts = []
        field_scores = []
        for line in field_lines:
            left_val = getattr(left, line.field_name, False)
            right_val = getattr(right, line.field_name, False)
            score = compare_values(left_val, right_val, line.match_type)
            field_scores.append((score, line.weight))
            if score >= 50:
                parts.append(f'{line.field_name}={score:.0f}%')
        return weighted_score(field_scores), ', '.join(parts)

    def cron_run_auto_scans(self):
        rules = self.env['rn.dup.rule'].search([('active', '=', True), ('auto_scan', '=', True)])
        for rule in rules:
            try:
                self.run_rule_scan(rule)
            except Exception:
                _logger.exception('Scheduled duplicate scan failed for rule %s', rule.id)
