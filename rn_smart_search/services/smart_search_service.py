# -*- coding: utf-8 -*-
"""Smart Search service layer."""

from __future__ import annotations

import hashlib
import logging
from datetime import timedelta
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.rn_smart_search.constants import (
    DEFAULT_AUTO_CLEAN_DAYS,
    DEFAULT_MAX_HISTORY,
    DEFAULT_REMEMBER_SEARCHES,
    DEFAULT_REMEMBER_VIEWED,
    HISTORY_TYPE_SEARCH,
    HISTORY_TYPE_VIEW,
    PARAM_AUTO_CLEAN_DAYS,
    PARAM_MAX_HISTORY,
    PARAM_REMEMBER_SEARCHES,
    PARAM_REMEMBER_VIEWED,
)

_logger = logging.getLogger(__name__)


class RnSmartSearchService(models.AbstractModel):
    _name = 'rn.smart.search.service'
    _description = 'Smart Search Service'

    @api.model
    def _param_bool(self, key: str, default: bool) -> bool:
        value = self.env['ir.config_parameter'].sudo().get_param(key, str(default))
        return str(value).lower() in ('1', 'true', 'yes')

    @api.model
    def _param_int(self, key: str, default: int) -> int:
        value = self.env['ir.config_parameter'].sudo().get_param(key, str(default))
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @api.model
    def _remember_viewed(self) -> bool:
        return self._param_bool(PARAM_REMEMBER_VIEWED, DEFAULT_REMEMBER_VIEWED)

    @api.model
    def _remember_searches(self) -> bool:
        return self._param_bool(PARAM_REMEMBER_SEARCHES, DEFAULT_REMEMBER_SEARCHES)

    @api.model
    def _max_history(self) -> int:
        return max(1, self._param_int(PARAM_MAX_HISTORY, DEFAULT_MAX_HISTORY))

    @api.model
    def _auto_clean_days(self) -> int:
        return max(1, self._param_int(PARAM_AUTO_CLEAN_DAYS, DEFAULT_AUTO_CLEAN_DAYS))

    @api.model
    def _normalize_query(self, query: str) -> str:
        return ' '.join((query or '').strip().lower().split())

    @api.model
    def _make_view_key(self, model: str, record_id: int) -> str:
        return f'view:{model}:{record_id}'

    @api.model
    def _make_search_key(self, query: str, model: str | None = None) -> str:
        normalized = self._normalize_query(query)
        digest = hashlib.sha1(normalized.encode('utf-8')).hexdigest()[:16]
        model_part = model or '*'
        return f'search:{model_part}:{digest}'

    @api.model
    def _resolve_label(self, model: str, record_id: int, label: str | None = None) -> str:
        if label:
            return label
        try:
            record = self.env[model].browse(record_id)
            if record.exists():
                return record.display_name
        except Exception as exc:  # noqa: BLE001 - best effort label lookup
            _logger.debug('Could not resolve label for %s(%s): %s', model, record_id, exc)
        return f'{model} #{record_id}'

    @api.model
    def _serialize_entry(self, entry) -> dict[str, Any]:
        return {
            'id': entry.id,
            'history_type': entry.history_type,
            'model': entry.model,
            'record_id': entry.record_id,
            'label': entry.label,
            'search_query': entry.search_query,
            'last_opened': fields.Datetime.to_string(entry.last_opened),
            'open_count': entry.open_count,
            'is_favorite': entry.is_favorite,
            'model_label': entry.model_label,
        }

    @api.model
    def _trim_history(self, user_id: int | None = None) -> None:
        History = self.env['rn.search.history']
        user = user_id or self.env.user.id
        max_entries = self._max_history()
        domain = [
            ('user_id', '=', user),
            ('is_favorite', '=', False),
        ]
        excess = History.search(domain, order='last_opened asc, id asc')
        if len(excess) <= max_entries:
            return
        to_remove = excess[: len(excess) - max_entries]
        to_remove.unlink()

    @api.model
    def _upsert_history(self, values: dict[str, Any]):
        History = self.env['rn.search.history']
        user = self.env.user
        entry_key = values['entry_key']
        existing = History.search([
            ('user_id', '=', user.id),
            ('entry_key', '=', entry_key),
        ], limit=1)
        now = fields.Datetime.now()
        if existing:
            write_vals = {
                'last_opened': now,
                'open_count': existing.open_count + 1,
            }
            for field in ('label', 'search_query', 'model', 'record_id', 'company_id'):
                if values.get(field):
                    write_vals[field] = values[field]
            existing.write(write_vals)
            self._trim_history(user.id)
            return existing
        values.update({
            'user_id': user.id,
            'company_id': values.get('company_id') or user.company_id.id,
            'last_opened': now,
            'open_count': 1,
        })
        entry = History.create(values)
        self._trim_history(user.id)
        return entry

    @api.model
    def log_view(self, model: str, record_id: int, label: str | None = None):
        """Track that the current user opened a business record."""
        if not self._remember_viewed() or not model or not record_id:
            return False
        if model not in self.env:
            return False
        resolved_label = self._resolve_label(model, record_id, label)
        return self._upsert_history({
            'history_type': HISTORY_TYPE_VIEW,
            'model': model,
            'record_id': record_id,
            'label': resolved_label,
            'entry_key': self._make_view_key(model, record_id),
        })

    @api.model
    def log_search(self, query: str, model: str | None = None):
        """Track a search query for the current user."""
        normalized = self._normalize_query(query)
        if not self._remember_searches() or not normalized:
            return False
        return self._upsert_history({
            'history_type': HISTORY_TYPE_SEARCH,
            'model': model,
            'record_id': 0,
            'label': normalized,
            'search_query': normalized,
            'entry_key': self._make_search_key(normalized, model),
        })

    @api.model
    def get_workspace_data(self) -> dict[str, Any]:
        """Return grouped history for the Smart Search workspace."""
        History = self.env['rn.search.history']
        base_domain = [('user_id', '=', self.env.user.id)]
        favorites = History.search(
            base_domain + [('is_favorite', '=', True)],
            order='last_opened desc, id desc',
            limit=20,
        )
        recent_views = History.search(
            base_domain + [('history_type', '=', HISTORY_TYPE_VIEW)],
            order='last_opened desc, id desc',
            limit=20,
        )
        recent_searches = History.search(
            base_domain + [('history_type', '=', HISTORY_TYPE_SEARCH)],
            order='last_opened desc, id desc',
            limit=20,
        )
        return {
            'favorites': [self._serialize_entry(item) for item in favorites],
            'recent_views': [self._serialize_entry(item) for item in recent_views],
            'recent_searches': [self._serialize_entry(item) for item in recent_searches],
            'settings': {
                'remember_viewed': self._remember_viewed(),
                'remember_searches': self._remember_searches(),
                'max_history': self._max_history(),
                'auto_clean_days': self._auto_clean_days(),
            },
        }

    @api.model
    def get_command_items(self, query: str = '') -> list[dict[str, Any]]:
        """Return command palette items from recent history."""
        History = self.env['rn.search.history']
        domain = [('user_id', '=', self.env.user.id)]
        normalized = self._normalize_query(query)
        if normalized:
            domain += [
                '|', '|',
                ('label', 'ilike', normalized),
                ('search_query', 'ilike', normalized),
                ('model_label', 'ilike', normalized),
            ]
        entries = History.search(domain, order='last_opened desc, id desc', limit=15)
        items = []
        for entry in entries:
            if entry.history_type == HISTORY_TYPE_VIEW:
                subtitle = entry.model_label or entry.model or ''
                name = entry.label
            else:
                subtitle = _('Recent search')
                name = entry.search_query or entry.label
            items.append({
                'id': entry.id,
                'name': name,
                'subtitle': subtitle,
                'history_type': entry.history_type,
                'is_favorite': entry.is_favorite,
            })
        return items

    @api.model
    def cleanup_stale_history(self):
        """Remove old non-favorite history entries."""
        cutoff = fields.Datetime.now() - timedelta(days=self._auto_clean_days())
        stale = self.env['rn.search.history'].sudo().search([
            ('last_opened', '<', cutoff),
            ('is_favorite', '=', False),
        ])
        count = len(stale)
        stale.unlink()
        _logger.info('Smart Search cleaned %s stale history entries.', count)
        return count

    @api.model
    def open_history_record(self, history_id: int):
        """Open a history entry and refresh its counters."""
        entry = self.env['rn.search.history'].browse(history_id)
        if not entry or not entry.exists():
            raise UserError(_('History entry not found.'))
        if entry.user_id != self.env.user:
            raise UserError(_('You can only open your own history entries.'))
        entry.write({
            'last_opened': fields.Datetime.now(),
            'open_count': entry.open_count + 1,
        })
        if entry.history_type == HISTORY_TYPE_VIEW and entry.model and entry.record_id:
            if entry.model not in self.env:
                raise UserError(_('The linked model is no longer available.'))
            record = self.env[entry.model].browse(entry.record_id)
            if not record.exists():
                raise UserError(_('The linked record no longer exists.'))
            return {
                'type': 'ir.actions.act_window',
                'name': entry.label,
                'res_model': entry.model,
                'view_mode': 'form',
                'res_id': entry.record_id,
                'target': 'current',
            }
        if entry.history_type == HISTORY_TYPE_SEARCH:
            action_domain = []
            if entry.model and entry.model in self.env:
                action_domain = self._search_domain_for_model(entry.model, entry.search_query)
            return {
                'type': 'ir.actions.act_window',
                'name': entry.search_query or entry.label,
                'res_model': entry.model or 'ir.ui.view',
                'view_mode': 'list,form' if entry.model else 'form',
                'domain': action_domain,
                'target': 'current',
            }
        raise UserError(_('This history entry cannot be opened.'))

    @api.model
    def _search_domain_for_model(self, model: str, query: str | None) -> list:
        normalized = self._normalize_query(query or '')
        if not normalized:
            return []
        if model == 'res.partner':
            return ['|', ('name', 'ilike', normalized), ('email', 'ilike', normalized)]
        if model == 'product.template':
            return [('name', 'ilike', normalized)]
        if model == 'crm.lead':
            return ['|', ('name', 'ilike', normalized), ('contact_name', 'ilike', normalized)]
        if model == 'sale.order':
            return ['|', ('name', 'ilike', normalized), ('partner_id.name', 'ilike', normalized)]
        if model == 'account.move':
            return ['|', ('name', 'ilike', normalized), ('partner_id.name', 'ilike', normalized)]
        return [('name', 'ilike', normalized)]

    @api.model
    def toggle_favorite(self, history_id: int) -> dict[str, Any]:
        entry = self.env['rn.search.history'].browse(history_id)
        entry.ensure_one()
        if entry.user_id != self.env.user:
            raise UserError(_('You can only update your own history entries.'))
        entry.is_favorite = not entry.is_favorite
        return self._serialize_entry(entry)

    @api.model
    def clear_history(self, history_type: str | None = None) -> int:
        domain = [
            ('user_id', '=', self.env.user.id),
            ('is_favorite', '=', False),
        ]
        if history_type:
            domain.append(('history_type', '=', history_type))
        entries = self.env['rn.search.history'].search(domain)
        count = len(entries)
        entries.unlink()
        return count
