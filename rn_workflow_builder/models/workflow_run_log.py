# -*- coding: utf-8 -*-
"""Per-step execution logs."""

from odoo import fields, models


class RnWorkflowRunLog(models.Model):
    """Audit log for each node executed in a run."""

    _name = 'rn.workflow.run.log'
    _description = 'Workflow Run Log'
    _order = 'sequence, id'

    run_id = fields.Many2one('rn.workflow.run', required=True, ondelete='cascade', index=True)
    node_id = fields.Many2one('rn.workflow.node', ondelete='set null')
    sequence = fields.Integer(default=10)
    node_name = fields.Char()
    node_type = fields.Selection(
        [
            ('trigger', 'Trigger'),
            ('condition', 'Condition'),
            ('action', 'Action'),
        ],
    )
    state = fields.Selection(
        [
            ('success', 'Success'),
            ('skipped', 'Skipped'),
            ('failed', 'Failed'),
        ],
        default='success',
        required=True,
    )
    message = fields.Text()
    executed_at = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one(
        related='run_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
