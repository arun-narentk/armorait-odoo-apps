# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .. import constants as bm_constants


class RnBookmark(models.Model):
    _name = 'rn.bookmark'
    _description = 'Universal Bookmark'
    _order = 'is_pinned desc, sequence, name, id'
    _rec_name = 'name'

    name = fields.Char(required=True, index=True)
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, index=True)
    bookmark_type = fields.Selection(bm_constants.BOOKMARK_TYPES, required=True, default='record', index=True)
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    action_id = fields.Many2one('ir.actions.actions', ondelete='set null')
    menu_id = fields.Many2one('ir.ui.menu', ondelete='set null')
    report_action_id = fields.Many2one('ir.actions.report', ondelete='set null')
    domain = fields.Text(default='[]')
    context = fields.Text(default='{}')
    folder_id = fields.Many2one('rn.bookmark.folder', ondelete='set null', index=True)
    tag_ids = fields.Many2many('rn.bookmark.tag', string='Tags')
    color = fields.Selection(bm_constants.BOOKMARK_COLORS, default='blue')
    icon = fields.Char(default='fa-star')
    note = fields.Text()
    sequence = fields.Integer(default=10, index=True)
    is_pinned = fields.Boolean(default=False, index=True)
    is_favorite = fields.Boolean(default=False, index=True)
    active = fields.Boolean(default=True)
    last_opened_at = fields.Datetime(index=True)
    open_count = fields.Integer(default=0)
    display_reference = fields.Char(compute='_compute_display_reference')

    @api.constrains('user_id', 'bookmark_type', 'res_model', 'res_id')
    def _check_record_bookmark_unique(self):
        for bookmark in self.filtered(lambda b: b.bookmark_type == 'record' and b.res_model and b.res_id):
            duplicate = self.search([
                ('id', '!=', bookmark.id),
                ('user_id', '=', bookmark.user_id.id),
                ('bookmark_type', '=', 'record'),
                ('res_model', '=', bookmark.res_model),
                ('res_id', '=', bookmark.res_id),
                ('active', '=', True),
            ], limit=1)
            if duplicate:
                raise ValidationError('This record is already bookmarked.')

    @api.depends('bookmark_type', 'res_model', 'res_id', 'action_id', 'menu_id')
    def _compute_display_reference(self):
        for bookmark in self:
            if bookmark.bookmark_type == 'record' and bookmark.res_model and bookmark.res_id:
                bookmark.display_reference = f'{bookmark.res_model},{bookmark.res_id}'
            elif bookmark.menu_id:
                bookmark.display_reference = bookmark.menu_id.display_name
            elif bookmark.action_id:
                bookmark.display_reference = bookmark.action_id.display_name
            else:
                bookmark.display_reference = bookmark.name

    def action_open_bookmark(self):
        self.ensure_one()
        return self.env['rn.bookmark.service'].open_bookmark(self)

    def action_pin(self):
        self.write({'is_pinned': True})

    def action_unpin(self):
        self.write({'is_pinned': False})

    def action_toggle_favorite(self):
        for bookmark in self:
            bookmark.is_favorite = not bookmark.is_favorite
