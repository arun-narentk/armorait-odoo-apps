# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .. import constants as bm_constants


class BookmarkFolder(models.Model):
    _name = 'rn.bookmark.folder'
    _description = 'Bookmark Folder'
    _order = 'sequence, name, id'

    name = fields.Char(required=True)
    parent_id = fields.Many2one('rn.bookmark.folder', ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    color = fields.Selection(bm_constants.BOOKMARK_COLORS, default='blue')
    icon = fields.Char(default='fa-folder')
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, index=True)
    active = fields.Boolean(default=True)
    bookmark_ids = fields.One2many('rn.bookmark', 'folder_id')
    bookmark_count = fields.Integer(compute='_compute_bookmark_count')

    @api.depends('bookmark_ids')
    def _compute_bookmark_count(self):
        grouped = self.env['rn.bookmark'].read_group(
            [('folder_id', 'in', self.ids), ('active', '=', True)],
            ['folder_id'],
            ['folder_id'],
            lazy=False,
        )
        counter = {row['folder_id'][0]: row.get('__count', 0) for row in grouped if row.get('folder_id')}
        for folder in self:
            folder.bookmark_count = counter.get(folder.id, 0)

    def action_open_bookmarks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'rn.bookmark',
            'view_mode': 'list,form',
            'domain': [('folder_id', '=', self.id), ('user_id', '=', self.env.user.id)],
        }
