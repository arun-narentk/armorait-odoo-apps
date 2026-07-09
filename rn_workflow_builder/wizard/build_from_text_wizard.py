# -*- coding: utf-8 -*-
"""Wizard to build workflow from plain English."""

from odoo import fields, models


class RnWorkflowBuildFromTextWizard(models.TransientModel):
    _name = 'rn.workflow.build.from.text.wizard'
    _description = 'Build Workflow from Text'

    prompt = fields.Text(required=True)
    model_id = fields.Many2one('ir.model', string='Target Model')
    workflow_id = fields.Many2one('rn.workflow', readonly=True)

    def action_build(self):
        self.ensure_one()
        wf_id = self.env['rn.workflow.ai.service'].build_from_text(
            self.prompt,
            model_name=self.model_id.model if self.model_id else None,
        )
        self.workflow_id = wf_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.workflow',
            'res_id': wf_id,
            'view_mode': 'form',
            'target': 'current',
        }
