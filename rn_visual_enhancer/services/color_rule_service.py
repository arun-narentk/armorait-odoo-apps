# -*- coding: utf-8 -*-

import logging

from odoo import models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from ..constants import COLOR_CSS_CLASS

_logger = logging.getLogger(__name__)
_RULE_CACHE = {}


_STATUS_CACHE = {}


class RnColorRuleService(models.AbstractModel):
    _name = "rn.color.rule.service"
    _description = "Visual Color Rule Service"

    def clear_rule_cache(self):
        _RULE_CACHE.clear()
        _STATUS_CACHE.clear()

    def _get_active_rules(self, model_name, company_id):
        cache_key = (self.env.cr.dbname, model_name, company_id)
        if cache_key not in _RULE_CACHE:
            domain = [("active", "=", True), ("model_name", "=", model_name)]
            if company_id:
                domain = expression.AND([domain, [("company_id", "=", company_id)]])
            rules = self.env["rn.color.rule"].sudo().search(
                domain, order="priority desc, id asc",
            )
            _RULE_CACHE[cache_key] = [
                {
                    "id": rule.id,
                    "domain": rule.domain,
                    "color": rule.color,
                    "icon": rule.icon,
                    "emoji": rule.emoji,
                    "label": rule.label,
                }
                for rule in rules
            ]
        return _RULE_CACHE[cache_key]

    def _parse_domain(self, domain_str):
        try:
            parsed_domain = safe_eval(domain_str or "[]")
        except Exception as exc:
            _logger.warning("Invalid color-rule domain %s: %s", domain_str, exc)
            return []
        if not isinstance(parsed_domain, (list, tuple)):
            _logger.warning("Color-rule domain did not evaluate to list/tuple: %s", domain_str)
            return []
        return list(parsed_domain)

    def _match_rules_for_records(self, model_name, record_ids):
        if model_name not in self.env or not record_ids:
            return {}
        model = self.env[model_name].sudo()
        company_id = self.env.company.id if "company_id" in model._fields else False
        rules = self._get_active_rules(model_name, company_id)
        matched_by_id = {}
        pending_ids = set(record_ids)
        for rule in rules:
            if not pending_ids:
                break
            parsed = self._parse_domain(rule["domain"])
            record_domain = expression.AND([[("id", "in", list(pending_ids))], parsed])
            matches = model.search(record_domain).ids
            for record_id in matches:
                if record_id in pending_ids:
                    matched_by_id[record_id] = rule
                    pending_ids.discard(record_id)
        return matched_by_id

    def _get_status_maps(self, model_name, company_id):
        cache_key = (self.env.cr.dbname, model_name, company_id, 'status')
        if cache_key not in _STATUS_CACHE:
            domain = [('active', '=', True), ('model_name', '=', model_name)]
            if company_id:
                domain = expression.AND([domain, [('company_id', '=', company_id)]])
            statuses = self.env['rn.visual.status'].sudo().search(domain, order='sequence, id')
            _STATUS_CACHE[cache_key] = [
                {
                    'field_name': status.field_name,
                    'field_value': status.field_value,
                    'emoji': status.emoji,
                    'icon': status.icon,
                    'color': status.color,
                    'label': status.label,
                }
                for status in statuses
            ]
        return _STATUS_CACHE[cache_key]

    def _status_tag_for_record(self, model, record, status_maps):
        for status in status_maps:
            field_name = status['field_name']
            if field_name not in model._fields:
                continue
            field = model._fields[field_name]
            raw_value = record[field_name]
            if field.type == 'selection':
                compare_value = raw_value
            else:
                compare_value = str(raw_value) if raw_value not in (False, None) else False
            if compare_value == status['field_value']:
                return {
                    'color': status['color'],
                    'icon': status['icon'],
                    'emoji': status['emoji'],
                    'label': status['label'] or str(compare_value),
                    'css_class': COLOR_CSS_CLASS.get(status['color'], ''),
                }
        return {}

    def get_tags_batch(self, model_name, record_ids):
        if not record_ids:
            return {}
        matched_by_id = self._match_rules_for_records(model_name, record_ids)
        model = self.env[model_name].sudo()
        company_id = self.env.company.id if 'company_id' in model._fields else False
        status_maps = self._get_status_maps(model_name, company_id)
        payload = {}
        for record_id in record_ids:
            rule = matched_by_id.get(record_id)
            if rule:
                payload[record_id] = {
                    'rule_id': rule['id'],
                    'color': rule['color'],
                    'icon': rule['icon'],
                    'emoji': rule.get('emoji'),
                    'label': rule['label'],
                    'css_class': COLOR_CSS_CLASS.get(rule['color'], ''),
                }
                continue
            record = model.browse(record_id)
            if record.exists() and status_maps:
                status_tag = self._status_tag_for_record(model, record, status_maps)
                if status_tag:
                    payload[record_id] = status_tag
                    continue
            payload[record_id] = {}
        return payload

    def get_tags_for_web(self, model_name, record_ids):
        tags = self.get_tags_batch(model_name, record_ids)
        return {str(record_id): tag for record_id, tag in tags.items()}

    def recompute_model_tags(self, model_name, company_id=False):
        if model_name not in self.env:
            return
        model = self.env[model_name].sudo()
        if "_rn_refresh_color_tags" not in model:
            return
        domain = []
        if company_id and "company_id" in model._fields:
            domain.append(("company_id", "=", company_id))
        records = model.search(domain)
        if records:
            records._rn_refresh_color_tags()
