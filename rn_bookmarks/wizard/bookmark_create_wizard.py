# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

from .. import constants as bm_constants


class BookmarkCreateWizard(models.TransientModel):
    _name = 'rn.bookmark.create.wizard'
    _description = 'Create Bookmark Wizard'

    bookmark_type = fields.Selection(
        selection=[t for t in bm_constants.BOOKMARK_TYPES if t[0] != 'record'],
        required=True,
        default='list',
    )
    name = fields.Char(required=True)
    folder_id = fields.Many2one('rn.bookmark.folder', domain="[('user_id', '=', uid)]")
    tag_ids = fields.Many2many('rn.bookmark.tag', domain="[('user_id', '=', uid)]")
    color = fields.Selection(bm_constants.BOOKMARK_COLORS, default='blue')
    note = fields.Text()
    is_pinned = fields.Boolean(default=False)
    is_favorite = fields.Boolean(default=False)
    res_model = fields.Char(string='Model')
    domain = fields.Text(default='[]')
    context_data = fields.Text(string='Context', default='{}')
    menu_id = fields.Many2one('ir.ui.menu')
    report_action_id = fields.Many2one('ir.actions.report')
    action_id = fields.Many2one('ir.actions.actions', string='Dashboard Action')

    @api.onchange('menu_id')
    def _onchange_menu_id(self):
        if self.menu_id and not self.name:
            self.name = self.menu_id.display_name

    @api.onchange('report_action_id')
    def _onchange_report_action_id(self):
        if self.report_action_id and not self.name:
            self.name = self.report_action_id.name

    @api.onchange('bookmark_type')
    def _onchange_bookmark_type(self):
        if self.bookmark_type == 'list' and not self.res_model:
            self.res_model = 'sale.order'

    def _validate_json_field(self, value, label):
        try:
            json.loads(value or '[]' if label == 'domain' else value or '{}')
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise UserError(f'Invalid {label} JSON: {exc}') from exc

    def action_create_bookmark(self):
        self.ensure_one()
        service = self.env['rn.bookmark.service']
        common_vals = {
            'name': self.name,
            'folder_id': self.folder_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'color': self.color,
            'note': self.note,
            'is_pinned': self.is_pinned,
            'is_favorite': self.is_favorite,
        }
        if self.bookmark_type == 'list':
            if not self.res_model:
                raise UserError('Select a model for the list bookmark.')
            self._validate_json_field(self.domain, 'domain')
            self._validate_json_field(self.context_data, 'context')
            bookmark = service.create_list_bookmark(
                self.name,
                self.res_model,
                domain=json.loads(self.domain or '[]'),
                context=json.loads(self.context_data or '{}'),
                folder_id=self.folder_id.id,
            )
            bookmark.write({
                'tag_ids': common_vals['tag_ids'],
                'color': self.color,
                'note': self.note,
                'is_pinned': self.is_pinned,
                'is_favorite': self.is_favorite,
            })
        elif self.bookmark_type == 'menu':
            if not self.menu_id:
                raise UserError('Select a menu to bookmark.')
            bookmark = service.create_menu_bookmark(self.menu_id, folder_id=self.folder_id.id)
            bookmark.write(common_vals)
        elif self.bookmark_type == 'report':
            if not self.report_action_id:
                raise UserError('Select a report to bookmark.')
            bookmark = service.create_report_bookmark(
                self.report_action_id, folder_id=self.folder_id.id,
            )
            bookmark.write(common_vals)
        elif self.bookmark_type == 'dashboard':
            if not self.action_id:
                raise UserError('Select a dashboard or client action to bookmark.')
            bookmark = self.env['rn.bookmark'].create({
                **common_vals,
                'bookmark_type': 'dashboard',
                'action_id': self.action_id.id,
                'res_model': getattr(self.action_id, 'res_model', False),
            })
        else:
            raise UserError('Unsupported bookmark type.')
        return {
            'type': 'ir.actions.act_window',
            'name': bookmark.name,
            'res_model': 'rn.bookmark',
            'res_id': bookmark.id,
            'view_mode': 'form',
            'target': 'current',
        }
