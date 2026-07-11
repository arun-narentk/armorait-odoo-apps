# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .. import constants as fm_constants


class FilterFolder(models.Model):
    _name = 'rn.filter.folder'
    _description = 'Filter Folder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'sequence, name, id'

    name = fields.Char(required=True, tracking=True)
    parent_id = fields.Many2one('rn.filter.folder', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('rn.filter.folder', 'parent_id')
    sequence = fields.Integer(default=10)
    color = fields.Selection(fm_constants.FILTER_COLORS, default='blue')
    icon = fields.Char(default='fa-folder')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, index=True)
    active = fields.Boolean(default=True)
    filter_ids = fields.One2many('ir.filters', 'rn_folder_id')
    filter_count = fields.Integer(compute='_compute_filter_count')
    owner_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True)
    is_team = fields.Boolean(string='Team Folder', default=False)

    @api.depends('filter_ids')
    def _compute_filter_count(self):
        grouped = self.env['ir.filters'].read_group(
            [('rn_folder_id', 'in', self.ids)],
            ['rn_folder_id'],
            ['rn_folder_id'],
            lazy=False,
        )
        counter = {row['rn_folder_id'][0]: row.get('__count', 0) for row in grouped if row.get('rn_folder_id')}
        for folder in self:
            folder.filter_count = counter.get(folder.id, 0)

    def action_open_filters(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'ir.filters',
            'view_mode': 'list,form',
            'domain': [('rn_folder_id', '=', self.id)],
            'context': {'default_rn_folder_id': self.id},
        }
