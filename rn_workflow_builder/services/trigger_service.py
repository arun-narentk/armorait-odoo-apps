# -*- coding: utf-8 -*-
"""Dispatch workflow triggers from ORM events."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnWorkflowTriggerService(models.AbstractModel):
    """Find and run matching workflows for model events."""

    _name = 'rn.workflow.trigger.service'
    _description = 'Workflow Trigger Service'

    def dispatch(self, model_name, res_id, event_type, record=None):
        domain = [
            ('state', '=', 'active'),
            ('model_name', '=', model_name),
            ('trigger_type', '=', event_type),
            ('company_id', '=', self.env.company.id),
        ]
        workflows = self.env['rn.workflow'].search(domain)
        if not workflows:
            return []
        Engine = self.env['rn.workflow.engine']
        run_ids = []
        payload = {}
        if record:
            payload = {
                'display_name': record.display_name,
                'id': record.id,
            }
        for wf in workflows:
            run_id = Engine.run_workflow(
                wf.id,
                trigger_model=model_name,
                trigger_res_id=res_id,
                trigger_payload=payload,
            )
            if run_id:
                run_ids.append(run_id)
        return run_ids

    def dispatch_webhook(self, token, payload=None):
        workflow = self.env['rn.workflow'].search([
            ('webhook_token', '=', token),
            ('trigger_type', '=', 'on_webhook'),
            ('state', '=', 'active'),
        ], limit=1)
        if not workflow:
            return False
        return self.env['rn.workflow.engine'].run_workflow(
            workflow.id,
            trigger_payload=payload or {},
        )
