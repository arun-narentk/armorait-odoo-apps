# -*- coding: utf-8 -*-
"""Mixin to attach smart notes to any business document."""

from odoo import api, fields, models, _


class RnNoteMixin(models.AbstractModel):
    _name = 'rn.note.mixin'
    _description = 'Smart Notes Mixin'

    smart_note_count = fields.Integer(compute='_compute_smart_note_count')
    smart_note_pinned_count = fields.Integer(compute='_compute_smart_note_count')

    def _compute_smart_note_count(self):
        if not self.ids:
            for record in self:
                record.smart_note_count = 0
                record.smart_note_pinned_count = 0
            return
        note_data = self.env['rn.smart.note'].read_group(
            [
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('active', '=', True),
            ],
            ['res_id', 'is_pinned'],
            ['res_id', 'is_pinned'],
            lazy=False,
        )
        counts = {record_id: {'total': 0, 'pinned': 0} for record_id in self.ids}
        for row in note_data:
            res_id = row['res_id']
            if res_id not in counts:
                continue
            counts[res_id]['total'] += row['__count']
            if row['is_pinned']:
                counts[res_id]['pinned'] += row['__count']
        for record in self:
            bucket = counts.get(record.id, {'total': 0, 'pinned': 0})
            record.smart_note_count = bucket['total']
            record.smart_note_pinned_count = bucket['pinned']

    def _get_notes(self):
        self.ensure_one()
        return self.env['rn.smart.note'].search(
            [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
                ('active', '=', True),
            ],
            order='is_pinned desc, priority_order desc, sequence, id desc',
        )

    def _add_note(self, values):
        self.ensure_one()
        return self.env['rn.smart.note.service'].add_note(self._name, self.id, values)

    def _pin_note(self, note):
        self.ensure_one()
        note.write({'is_pinned': True})

    def action_view_smart_notes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Notes'),
            'res_model': 'rn.smart.note',
            'view_mode': 'kanban,list,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_company_id': self.company_id.id if 'company_id' in self._fields else self.env.company.id,
            },
        }

    def get_smart_notes_panel_data(self):
        self.ensure_one()
        return self.env['rn.smart.note'].get_panel_data(self._name, self.id)
