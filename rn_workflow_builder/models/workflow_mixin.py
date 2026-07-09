# -*- coding: utf-8 -*-
"""Mixin to fire workflow triggers from business documents."""

from odoo import models


class RnWorkflowMixin(models.AbstractModel):
    """Call workflow engine on create/write when workflows are active."""

    _name = 'rn.workflow.mixin'
    _description = 'Workflow Trigger Mixin'

    def _rn_workflow_trigger(self, event_type):
        if self.env.context.get('rn_workflow_skip'):
            return
        Trigger = self.env['rn.workflow.trigger.service']
        for record in self:
            Trigger.dispatch(
                model_name=record._name,
                res_id=record.id,
                event_type=event_type,
                record=record,
            )

    def create(self, vals_list):
        records = super().create(vals_list)
        records._rn_workflow_trigger('on_create')
        return records

    def write(self, vals):
        res = super().write(vals)
        self._rn_workflow_trigger('on_write')
        return res
