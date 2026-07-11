# -*- coding: utf-8 -*-
"""Mixin to open the name suggestion wizard."""

from odoo import models, _


class RnNameMixin(models.AbstractModel):
    _name = 'rn.name.mixin'
    _description = 'Name Assistant Mixin'

    def action_suggest_name(self):
        self.ensure_one()
        return self.env['rn.name.generator.wizard'].open_for_record(self._name, self.id)

    def action_batch_suggest_names(self):
        active_ids = self.env.context.get('active_ids', self.ids)
        active_model = self.env.context.get('active_model', self._name)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate Suggested Names'),
            'res_model': 'rn.name.batch.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': active_model,
                'default_res_ids': ','.join(str(i) for i in active_ids),
            },
        }
