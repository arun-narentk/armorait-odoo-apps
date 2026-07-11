# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .. import constants as fm_constants


class IrFilters(models.Model):
    _inherit = 'ir.filters'

    rn_folder_id = fields.Many2one('rn.filter.folder', string='Folder', index=True, ondelete='set null')
    rn_is_pinned = fields.Boolean(string='Pinned', default=False, index=True)
    rn_is_favorite = fields.Boolean(string='Favorite', default=False, index=True)
    rn_color = fields.Selection(fm_constants.FILTER_COLORS, string='Color Tag')
    rn_share_type = fields.Selection(fm_constants.SHARE_TYPES, string='Share Type', default='private', index=True)
    rn_icon = fields.Char(string='Icon')
    rn_sequence = fields.Integer(string='Sequence', default=10, index=True)
    rn_owner_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user, index=True)
    rn_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, index=True)
    rn_usage_count = fields.Integer(string='Used', compute='_compute_rn_usage_stats', store=True)
    rn_last_used_at = fields.Datetime(string='Last Used', compute='_compute_rn_usage_stats', store=True)
    rn_history_ids = fields.One2many('rn.filter.history', 'filter_id')

    @api.depends('rn_history_ids.used_at')
    def _compute_rn_usage_stats(self):
        grouped = self.env['rn.filter.history'].read_group(
            [('filter_id', 'in', self.ids)],
            ['filter_id', 'used_at:max'],
            ['filter_id'],
            lazy=False,
        )
        stats = {row['filter_id'][0]: row for row in grouped if row.get('filter_id')}
        for record in self:
            row = stats.get(record.id, {})
            record.rn_usage_count = row.get('__count', 0)
            record.rn_last_used_at = row.get('used_at_max') or row.get('used_at')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('rn_owner_id'):
                vals['rn_owner_id'] = self.env.user.id
            if vals.get('rn_share_type') == 'global':
                vals.setdefault('user_ids', [(5, 0, 0)])
            elif vals.get('rn_share_type') == 'private':
                vals.setdefault('user_ids', [(6, 0, [self.env.user.id])])
        return super().create(vals_list)

    def action_pin(self):
        self.write({'rn_is_pinned': True})

    def action_unpin(self):
        self.write({'rn_is_pinned': False})

    def action_mark_favorite(self):
        self.write({'rn_is_favorite': True, 'rn_share_type': 'favorite'})

    def action_log_usage(self):
        service = self.env['rn.filter.service']
        for record in self:
            service.log_filter_usage(record, source='manager')
        return True

    def action_open_duplicates(self):
        self.ensure_one()
        duplicates = self.env['rn.filter.service'].find_duplicates(self)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Possible Duplicates',
            'res_model': 'ir.filters',
            'view_mode': 'list,form',
            'domain': [('id', 'in', duplicates.ids)],
        }

    @api.model
    def get_filters(self, model, action_id=None, embedded_action_id=None, embedded_parent_res_id=None):
        result = super().get_filters(
            model,
            action_id=action_id,
            embedded_action_id=embedded_action_id,
            embedded_parent_res_id=embedded_parent_res_id,
        )
        if self.env.context.get('rn_filter_manager_skip_log'):
            return result
        filters = self.browse([item['id'] for item in result if item.get('id')])
        if filters:
            self.env['rn.filter.service'].log_filter_usage(filters, source='search')
        return result
