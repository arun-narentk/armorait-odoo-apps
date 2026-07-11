# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class RnDiffMixin(models.AbstractModel):
    _name = 'rn.diff.mixin'
    _description = 'Field Diff Mixin'

    field_diff_count = fields.Integer(compute='_compute_field_diff_count')

    def _compute_field_diff_count(self):
        Diff = self.env['rn.field.diff']
        if not self.ids:
            for record in self:
                record.field_diff_count = 0
            return
        grouped = Diff.read_group(
            domain=[('model', '=', self._name), ('res_id', 'in', self.ids)],
            fields=['res_id'],
            groupby=['res_id'],
        )
        counts = {}
        for item in grouped:
            key = item.get('res_id')
            if isinstance(key, tuple):
                key = key[0]
            counts[key] = item.get('res_id_count', item.get('__count', 0))
        for record in self:
            record.field_diff_count = counts.get(record.id, 0)

    def action_view_field_diff_history(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('rn_field_diff.action_rn_field_diff')
        action['domain'] = [('model', '=', self._name), ('res_id', '=', self.id)]
        action['context'] = {
            'default_model': self._name,
            'default_res_id': self.id,
            'search_default_group_changed_on': 1,
        }
        summary = self.env['rn.field.diff.service'].get_summary(self._name, self.id)
        action['display_name'] = _('%s Changes (%s)') % (self.display_name, summary['total'])
        return action

    def action_open_diff_comparison(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Field Differences'),
            'res_model': 'rn.field.diff',
            'view_mode': 'list,form',
            'domain': [('model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'create': False},
            'target': 'new',
        }

    def action_export_field_diffs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Export Field Differences'),
            'res_model': 'rn.field.diff.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': self._name,
                'default_res_id': self.id,
            },
        }
