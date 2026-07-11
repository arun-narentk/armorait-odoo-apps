# -*- coding: utf-8 -*-
import json
import logging
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FilterService(models.AbstractModel):
    _name = 'rn.filter.service'
    _description = 'Filter Manager Service'

    def _recent_limit(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('rn_filter_manager.recent_limit', 50) or 50)

    def log_filter_usage(self, filters, source='manager'):
        remember = self.env['ir.config_parameter'].sudo().get_param('rn_filter_manager.remember_searches', 'True')
        if remember not in ('1', 'True', 'true'):
            return True
        History = self.env['rn.filter.history'].sudo()
        now = fields.Datetime.now()
        for filt in filters:
            History.create({
                'filter_id': filt.id,
                'user_id': self.env.user.id,
                'model_id': filt.model_id,
                'used_at': now,
                'source': source,
                'company_id': filt.rn_company_id.id or self.env.company.id,
            })
        self._cleanup_recent_history()
        return True

    def _cleanup_recent_history(self):
        limit = self._recent_limit()
        domain = [('user_id', '=', self.env.user.id)]
        history = self.env['rn.filter.history'].search(domain, order='used_at desc, id desc')
        if len(history) <= limit:
            return
        (history[limit:]).unlink()

    def find_duplicates(self, filter_record):
        filter_record.ensure_one()
        enabled = self.env['ir.config_parameter'].sudo().get_param('rn_filter_manager.duplicate_detection', 'True')
        if enabled not in ('1', 'True', 'true'):
            return self.env['ir.filters']
        domain = [
            ('id', '!=', filter_record.id),
            ('model_id', '=', filter_record.model_id),
            ('domain', '=', filter_record.domain),
        ]
        exact = self.env['ir.filters'].search(domain)
        name_domain = [
            ('id', '!=', filter_record.id),
            ('model_id', '=', filter_record.model_id),
            ('name', 'ilike', filter_record.name),
        ]
        fuzzy = self.env['ir.filters'].search(name_domain)
        return exact | fuzzy

    def suggest_pin(self, user=None):
        user = user or self.env.user
        since = fields.Datetime.now() - timedelta(days=7)
        grouped = self.env['rn.filter.history'].read_group(
            [('user_id', '=', user.id), ('used_at', '>=', since)],
            ['filter_id'],
            ['filter_id'],
            lazy=False,
        )
        suggestions = []
        for row in grouped:
            count = row.get('__count', 0)
            if count < 5 or not row.get('filter_id'):
                continue
            filt = self.env['ir.filters'].browse(row['filter_id'][0])
            if filt.exists() and not filt.rn_is_pinned:
                suggestions.append({'filter_id': filt.id, 'name': filt.name, 'usage_count': count})
        return sorted(suggestions, key=lambda item: item['usage_count'], reverse=True)[:5]

    def export_filters(self, filters):
        folders = filters.mapped('rn_folder_id')
        folder_payload = []
        for folder in folders:
            folder_payload.append({
                'name': folder.name,
                'color': folder.color,
                'icon': folder.icon,
                'sequence': folder.sequence,
                'is_team': folder.is_team,
            })
        filter_payload = []
        for filt in filters:
            filter_payload.append({
                'name': filt.name,
                'model_id': filt.model_id,
                'domain': filt.domain,
                'context': filt.context,
                'sort': filt.sort,
                'folder_name': filt.rn_folder_id.name if filt.rn_folder_id else False,
                'rn_is_pinned': filt.rn_is_pinned,
                'rn_is_favorite': filt.rn_is_favorite,
                'rn_color': filt.rn_color,
                'rn_share_type': filt.rn_share_type,
                'rn_icon': filt.rn_icon,
                'rn_sequence': filt.rn_sequence,
            })
        return {
            'version': '19.0.1.0.0',
            'module': 'rn_filter_manager',
            'folders': folder_payload,
            'filters': filter_payload,
        }

    def import_filters(self, payload, mode='merge'):
        if not isinstance(payload, dict):
            raise UserError('Invalid JSON payload.')
        folder_map = {}
        Folder = self.env['rn.filter.folder'].sudo()
        for folder_data in payload.get('folders', []):
            folder = Folder.search([
                ('name', '=', folder_data.get('name')),
                ('company_id', '=', self.env.company.id),
            ], limit=1)
            if folder and mode == 'skip_existing':
                folder_map[folder_data['name']] = folder
                continue
            vals = {
                'name': folder_data.get('name'),
                'color': folder_data.get('color') or 'blue',
                'icon': folder_data.get('icon') or 'fa-folder',
                'sequence': folder_data.get('sequence', 10),
                'is_team': folder_data.get('is_team', False),
                'owner_id': self.env.user.id,
                'company_id': self.env.company.id,
            }
            if folder:
                folder.write(vals)
            else:
                folder = Folder.create(vals)
            folder_map[folder.name] = folder

        created = self.env['ir.filters']
        for item in payload.get('filters', []):
            existing = self.env['ir.filters'].search([
                ('name', '=', item.get('name')),
                ('model_id', '=', item.get('model_id')),
                ('domain', '=', item.get('domain')),
            ], limit=1)
            if existing and mode == 'skip_existing':
                continue
            folder = folder_map.get(item.get('folder_name')) if item.get('folder_name') else False
            vals = {
                'name': item.get('name'),
                'model_id': item.get('model_id'),
                'domain': item.get('domain', '[]'),
                'context': item.get('context', '{}'),
                'sort': item.get('sort', '[]'),
                'rn_folder_id': folder.id if folder else False,
                'rn_is_pinned': item.get('rn_is_pinned', False),
                'rn_is_favorite': item.get('rn_is_favorite', False),
                'rn_color': item.get('rn_color'),
                'rn_share_type': item.get('rn_share_type', 'private'),
                'rn_icon': item.get('rn_icon'),
                'rn_sequence': item.get('rn_sequence', 10),
                'rn_owner_id': self.env.user.id,
                'rn_company_id': self.env.company.id,
                'user_ids': [(6, 0, [self.env.user.id])],
            }
            if existing and mode == 'merge':
                existing.write(vals)
                created |= existing
            else:
                created |= self.env['ir.filters'].create(vals)
        return created
