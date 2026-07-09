# -*- coding: utf-8 -*-
"""Workflow execution engine."""

import logging
import time

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnWorkflowEngine(models.AbstractModel):
    """Execute workflow nodes in sequence with branching."""

    _name = 'rn.workflow.engine'
    _description = 'Workflow Execution Engine'

    def _log_step(self, run, node, state, message=''):
        return self.env['rn.workflow.run.log'].create({
            'run_id': run.id,
            'node_id': node.id if node else False,
            'node_name': node.name if node else '',
            'node_type': node.node_type if node else 'trigger',
            'state': state,
            'message': message,
        })

    def run_workflow(self, workflow_id, trigger_model=None, trigger_res_id=0, trigger_payload=None):
        workflow = self.env['rn.workflow'].browse(workflow_id)
        if not workflow.exists() or workflow.state != 'active':
            return False

        start = time.time()
        run = self.env['rn.workflow.run'].create({
            'workflow_id': workflow.id,
            'trigger_model': trigger_model or workflow.model_name or '',
            'trigger_res_id': trigger_res_id or 0,
            'state': 'running',
        })
        context = {
            'record_model': trigger_model or workflow.model_name,
            'record_id': trigger_res_id,
            'payload': trigger_payload or {},
            'company_id': workflow.company_id.id,
        }
        Condition = self.env['rn.workflow.condition.service']
        Action = self.env['rn.workflow.action.service']

        try:
            nodes = workflow.node_ids.filtered(lambda n: n.active).sorted('sequence')
            if not nodes:
                self._log_step(run, False, 'skipped', 'No nodes configured.')
            for node in nodes:
                if node.node_type == 'condition':
                    passed = Condition.evaluate(node, context)
                    self._log_step(
                        run, node, 'success',
                        f'Condition {"passed" if passed else "failed"}.',
                    )
                    if not passed and node.branch_false_id:
                        continue
                    if passed and node.branch_true_id:
                        continue
                elif node.node_type == 'action':
                    result = Action.execute(node, context)
                    self._log_step(run, node, 'success', result or 'Action completed.')
            run.write({
                'state': 'done',
                'end_time': fields.Datetime.now(),
                'duration_ms': int((time.time() - start) * 1000),
            })
        except Exception as exc:
            _logger.exception('Workflow run failed: %s', workflow.name)
            run.write({
                'state': 'failed',
                'end_time': fields.Datetime.now(),
                'duration_ms': int((time.time() - start) * 1000),
                'error_message': str(exc),
            })
            settings = workflow.company_id._get_workflow_settings()
            if settings.retry_failed_runs and run.retry_count < settings.max_retry_count:
                run.state = 'retry'
        return run.id

    def retry_failed_runs(self, company_id=None):
        company_id = company_id or self.env.company.id
        runs = self.env['rn.workflow.run'].search([
            ('state', '=', 'retry'),
            ('company_id', '=', company_id),
        ], limit=50)
        for run in runs:
            run.retry_count += 1
            self.run_workflow(
                run.workflow_id.id,
                trigger_model=run.trigger_model,
                trigger_res_id=run.trigger_res_id,
            )
        return len(runs)

    def get_designer_data(self, workflow_id):
        workflow = self.env['rn.workflow'].browse(workflow_id)
        if not workflow.exists():
            return {}
        return {
            'workflow': {
                'id': workflow.id,
                'name': workflow.name,
                'state': workflow.state,
                'trigger_type': workflow.trigger_type,
                'model': workflow.model_name or '',
            },
            'nodes': [
                {
                    'id': n.id,
                    'name': n.name,
                    'sequence': n.sequence,
                    'node_type': n.node_type,
                    'action_type': n.action_type or '',
                    'parent_id': n.parent_id.id or False,
                }
                for n in workflow.node_ids.sorted('sequence')
            ],
        }
