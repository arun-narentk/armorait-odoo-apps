# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Base(models.AbstractModel):
    _inherit = 'base'

    rn_bookmark_count = fields.Integer(string='Bookmarks', compute='_compute_rn_bookmark_count')
    rn_is_bookmarked = fields.Boolean(string='Bookmarked', compute='_compute_rn_bookmark_count')

    def _compute_rn_bookmark_count(self):
        if not self.ids:
            for record in self:
                record.rn_bookmark_count = 0
                record.rn_is_bookmarked = False
            return
        grouped = self.env['rn.bookmark'].read_group(
            [
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('user_id', '=', self.env.user.id),
                ('bookmark_type', '=', 'record'),
                ('active', '=', True),
            ],
            ['res_id'],
            ['res_id'],
            lazy=False,
        )
        counter = {row['res_id']: row.get('__count', 0) for row in grouped}
        for record in self:
            record.rn_bookmark_count = counter.get(record.id, 0)
            record.rn_is_bookmarked = bool(counter.get(record.id))

    def action_toggle_rn_bookmark(self):
        service = self.env['rn.bookmark.service']
        for record in self:
            service.toggle_record_bookmark(record)
        return True

    def action_open_rn_bookmarks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bookmarks',
            'res_model': 'rn.bookmark',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
            ],
        }
