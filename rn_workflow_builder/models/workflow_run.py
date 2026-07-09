# -*- coding: utf-8 -*-
"""Workflow execution runs."""

from odoo import api, fields, models


class RnWorkflowRun(models.Model):
    """Single workflow execution instance."""

    _name = 'rn.workflow.run'
    _description = 'Workflow Run'
    _inherit = ['mail.thread']
    _order = 'start_time desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    workflow_id = fields.Many2one('rn.workflow', required=True, ondelete='cascade', index=True)
    state = fields.Selection(
        [
            ('running', 'Running'),
            ('done', 'Done'),
            ('failed', 'Failed'),
            ('retry', 'Retry Queue'),
        ],
        default='running',
        required=True,
        tracking=True,
    )
    trigger_model = fields.Char(index=True)
    trigger_res_id = fields.Integer(index=True)
    start_time = fields.Datetime(default=fields.Datetime.now, required=True)
    end_time = fields.Datetime()
    duration_ms = fields.Integer(string='Duration (ms)')
    error_message = fields.Text()
    retry_count = fields.Integer(default=0)
    log_ids = fields.One2many('rn.workflow.run.log', 'run_id')
    company_id = fields.Many2one(
        related='workflow_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.workflow.run') or 'RUN'
        return super().create(vals_list)
