# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class BookmarkController(http.Controller):

    @http.route('/rn/bookmark/health', type='json', auth='user')
    def health(self):
        service = request.env['rn.bookmark.service']
        return {
            'status': 'ok',
            'module': 'rn_bookmarks',
            'stats': service.get_dashboard_stats(),
        }

    @http.route('/rn/bookmark/sidebar', type='json', auth='user')
    def sidebar(self, search=None, limit=200):
        return request.env['rn.bookmark.service'].get_sidebar_data(search=search, limit=limit)

    @http.route('/rn/bookmark/toggle', type='json', auth='user')
    def toggle(self, res_model, res_id, note=None, folder_id=None):
        record = request.env[res_model].browse(res_id)
        if not record.exists():
            return {'error': 'Record not found'}
        return request.env['rn.bookmark.service'].toggle_record_bookmark(
            record, note=note, folder_id=folder_id,
        )

    @http.route('/rn/bookmark/open/<int:bookmark_id>', type='json', auth='user')
    def open_bookmark(self, bookmark_id):
        bookmark = request.env['rn.bookmark'].browse(bookmark_id)
        if not bookmark.exists() or bookmark.user_id != request.env.user:
            return {'error': 'Bookmark not found'}
        action = request.env['rn.bookmark.service'].open_bookmark(bookmark)
        return {'action': action}

    @http.route('/rn/bookmark/move', type='json', auth='user')
    def move(self, bookmark_id, folder_id=None, sequence=None):
        request.env['rn.bookmark.service'].move_bookmark(bookmark_id, folder_id=folder_id, sequence=sequence)
        return {'status': 'ok'}

    @http.route('/rn/bookmark/state', type='json', auth='user')
    def state(self, res_model, res_id):
        return request.env['rn.bookmark.service'].get_current_context_bookmark_state(res_model, res_id)
