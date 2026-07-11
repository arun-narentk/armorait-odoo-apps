# -*- coding: utf-8 -*-
import json
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BookmarkService(models.AbstractModel):
    _name = 'rn.bookmark.service'
    _description = 'Bookmark Service'

    @api.model
    def _safe_json_loads(self, value, default):
        if not value:
            return default
        try:
            return json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return default

    @api.model
    def _get_record_display_name(self, model_name, res_id):
        if not model_name or not res_id:
            return 'Bookmark'
        try:
            record = self.env[model_name].browse(res_id).exists()
            return record.display_name if record else f'{model_name} #{res_id}'
        except Exception:
            _logger.debug('Could not resolve display name for %s,%s', model_name, res_id)
            return f'{model_name} #{res_id}'

    @api.model
    def toggle_record_bookmark(self, record, note=None, folder_id=None):
        model_name = record._name
        res_id = record.id
        Bookmark = self.env['rn.bookmark']
        existing = Bookmark.search([
            ('user_id', '=', self.env.user.id),
            ('bookmark_type', '=', 'record'),
            ('res_model', '=', model_name),
            ('res_id', '=', res_id),
            ('active', '=', True),
        ], limit=1)
        if existing:
            existing.unlink()
            return {'bookmarked': False, 'bookmark_id': False}
        vals = {
            'name': record.display_name,
            'bookmark_type': 'record',
            'res_model': model_name,
            'res_id': res_id,
            'note': note,
            'folder_id': folder_id,
        }
        bookmark = Bookmark.create(vals)
        return {'bookmarked': True, 'bookmark_id': bookmark.id}

    @api.model
    def create_list_bookmark(self, name, res_model, domain=None, context=None, folder_id=None):
        return self.env['rn.bookmark'].create({
            'name': name,
            'bookmark_type': 'list',
            'res_model': res_model,
            'domain': json.dumps(domain or []),
            'context': json.dumps(context or {}),
            'folder_id': folder_id,
        })

    @api.model
    def create_menu_bookmark(self, menu, folder_id=None):
        menu = menu if hasattr(menu, 'id') else self.env['ir.ui.menu'].browse(menu)
        if not menu.exists():
            raise UserError('Menu not found.')
        return self.env['rn.bookmark'].create({
            'name': menu.display_name,
            'bookmark_type': 'menu',
            'menu_id': menu.id,
            'action_id': menu.action.id if menu.action else False,
            'res_model': menu.action.res_model if menu.action and hasattr(menu.action, 'res_model') else False,
            'folder_id': folder_id,
        })

    @api.model
    def create_report_bookmark(self, report_action, folder_id=None):
        report = report_action if hasattr(report_action, 'id') else self.env['ir.actions.report'].browse(report_action)
        if not report.exists():
            raise UserError('Report not found.')
        return self.env['rn.bookmark'].create({
            'name': report.name,
            'bookmark_type': 'report',
            'report_action_id': report.id,
            'res_model': report.model,
            'folder_id': folder_id,
        })

    @api.model
    def open_bookmark(self, bookmark):
        bookmark = bookmark if hasattr(bookmark, 'id') else self.env['rn.bookmark'].browse(bookmark)
        if not bookmark.exists():
            raise UserError('Bookmark not found.')
        bookmark.sudo().write({
            'last_opened_at': fields.Datetime.now(),
            'open_count': bookmark.open_count + 1,
        })
        if bookmark.bookmark_type == 'record':
            return {
                'type': 'ir.actions.act_window',
                'name': bookmark.name,
                'res_model': bookmark.res_model,
                'res_id': bookmark.res_id,
                'view_mode': 'form',
                'target': 'current',
            }
        if bookmark.bookmark_type == 'list':
            return {
                'type': 'ir.actions.act_window',
                'name': bookmark.name,
                'res_model': bookmark.res_model,
                'view_mode': 'list,form',
                'domain': self._safe_json_loads(bookmark.domain, []),
                'context': self._safe_json_loads(bookmark.context, {}),
                'target': 'current',
            }
        if bookmark.bookmark_type == 'menu' and bookmark.menu_id:
            return bookmark.menu_id.action._get_action_dict() if bookmark.menu_id.action else {
                'type': 'ir.actions.act_window',
                'name': bookmark.name,
                'res_model': bookmark.res_model,
                'view_mode': 'list,form',
                'target': 'current',
            }
        if bookmark.bookmark_type == 'report' and bookmark.report_action_id:
            return bookmark.report_action_id.report_action()
        if bookmark.bookmark_type == 'dashboard' and bookmark.action_id:
            return bookmark.action_id._get_action_dict()
        raise UserError('This bookmark cannot be opened.')

    @api.model
    def get_sidebar_data(self, search=None, limit=200):
        domain = [('user_id', '=', self.env.user.id), ('active', '=', True)]
        if search:
            domain += ['|', ('name', 'ilike', search), ('note', 'ilike', search)]
        bookmarks = self.env['rn.bookmark'].search(domain, limit=limit)
        folders = self.env['rn.bookmark.folder'].search([
            ('user_id', '=', self.env.user.id),
            ('active', '=', True),
        ], order='sequence, name')
        pinned = bookmarks.filtered('is_pinned')
        favorites = bookmarks.filtered('is_favorite')
        recent = bookmarks.sorted('write_date', reverse=True)[:20]
        return {
            'pinned': [self._serialize_bookmark(b) for b in pinned],
            'favorites': [self._serialize_bookmark(b) for b in favorites],
            'recent': [self._serialize_bookmark(b) for b in recent],
            'folders': [{
                'id': folder.id,
                'name': folder.name,
                'color': folder.color,
                'icon': folder.icon,
                'bookmarks': [self._serialize_bookmark(b) for b in bookmarks.filtered(lambda x: x.folder_id == folder)],
            } for folder in folders],
            'unfiled': [self._serialize_bookmark(b) for b in bookmarks.filtered(lambda x: not x.folder_id)],
            'stats': self.get_dashboard_stats(),
        }

    @api.model
    def _serialize_bookmark(self, bookmark):
        return {
            'id': bookmark.id,
            'name': bookmark.name,
            'bookmark_type': bookmark.bookmark_type,
            'res_model': bookmark.res_model,
            'res_id': bookmark.res_id,
            'color': bookmark.color,
            'icon': bookmark.icon,
            'note': bookmark.note or '',
            'is_pinned': bookmark.is_pinned,
            'is_favorite': bookmark.is_favorite,
            'folder_id': bookmark.folder_id.id if bookmark.folder_id else False,
            'tag_ids': bookmark.tag_ids.ids,
            'sequence': bookmark.sequence,
        }

    @api.model
    def get_dashboard_stats(self):
        Bookmark = self.env['rn.bookmark']
        Folder = self.env['rn.bookmark.folder']
        user_domain = [('user_id', '=', self.env.user.id), ('active', '=', True)]
        return {
            'total': Bookmark.search_count(user_domain),
            'favorites': Bookmark.search_count(user_domain + [('is_favorite', '=', True)]),
            'pinned': Bookmark.search_count(user_domain + [('is_pinned', '=', True)]),
            'folders': Folder.search_count([('user_id', '=', self.env.user.id), ('active', '=', True)]),
        }

    @api.model
    def get_recent_groups(self):
        Bookmark = self.env['rn.bookmark']
        now = fields.Datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=7)
        user_domain = [('user_id', '=', self.env.user.id), ('active', '=', True)]
        bookmarks = Bookmark.search(user_domain, order='write_date desc', limit=100)
        groups = {'today': [], 'yesterday': [], 'last_week': [], 'older': []}
        for bookmark in bookmarks:
            dt = bookmark.write_date or bookmark.create_date
            if not dt:
                groups['older'].append(self._serialize_bookmark(bookmark))
                continue
            if dt >= today_start:
                groups['today'].append(self._serialize_bookmark(bookmark))
            elif dt >= yesterday_start:
                groups['yesterday'].append(self._serialize_bookmark(bookmark))
            elif dt >= week_start:
                groups['last_week'].append(self._serialize_bookmark(bookmark))
            else:
                groups['older'].append(self._serialize_bookmark(bookmark))
        return groups

    @api.model
    def move_bookmark(self, bookmark_id, folder_id=None, sequence=None):
        bookmark = self.env['rn.bookmark'].browse(bookmark_id)
        if not bookmark.exists() or bookmark.user_id != self.env.user:
            raise UserError('Bookmark not found.')
        vals = {}
        if folder_id is not None:
            vals['folder_id'] = folder_id or False
        if sequence is not None:
            vals['sequence'] = sequence
        if vals:
            bookmark.write(vals)
        return True

    @api.model
    def get_bookmark_states_batch(self, res_model, res_ids):
        if not res_model or not res_ids:
            return {}
        bookmarks = self.env['rn.bookmark'].search([
            ('user_id', '=', self.env.user.id),
            ('bookmark_type', '=', 'record'),
            ('res_model', '=', res_model),
            ('res_id', 'in', list(res_ids)),
            ('active', '=', True),
        ])
        bookmarked_ids = set(bookmarks.mapped('res_id'))
        return {str(res_id): res_id in bookmarked_ids for res_id in res_ids}

    @api.model
    def reorder_bookmarks(self, bookmark_ids):
        if not bookmark_ids:
            return True
        Bookmark = self.env['rn.bookmark']
        sequence = 10
        for bookmark_id in bookmark_ids:
            bookmark = Bookmark.browse(bookmark_id)
            if bookmark.exists() and bookmark.user_id == self.env.user:
                bookmark.sequence = sequence
                sequence += 10
        return True

    @api.model
    def get_current_context_bookmark_state(self, res_model, res_id):
        if not res_model or not res_id:
            return {'bookmarked': False, 'bookmark_id': False}
        bookmark = self.env['rn.bookmark'].search([
            ('user_id', '=', self.env.user.id),
            ('bookmark_type', '=', 'record'),
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
            ('active', '=', True),
        ], limit=1)
        return {
            'bookmarked': bool(bookmark),
            'bookmark_id': bookmark.id if bookmark else False,
        }
