# -*- coding: utf-8 -*-
"""Workflow definition."""

from odoo import api, fields, models


class RnWorkflow(models.Model):
    """Automation workflow graph root."""

    _name = 'rn.workflow'
    _description = 'Automation Workflow'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('paused', 'Paused'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    trigger_type = fields.Selection(
        [
            ('on_create', 'Record Created'),
            ('on_write', 'Record Updated'),
            ('on_schedule', 'Scheduled'),
            ('on_webhook', 'Webhook'),
            ('manual', 'Manual'),
        ],
        default='on_create',
        required=True,
    )
    model_id = fields.Many2one('ir.model', string='Target Model', ondelete='set null')
    model_name = fields.Char(related='model_id.model', store=True, readonly=True)
    schedule_interval = fields.Integer(string='Schedule Every (minutes)', default=60)
    webhook_token = fields.Char(copy=False, readonly=True)
    node_ids = fields.One2many('rn.workflow.node', 'workflow_id')
    run_ids = fields.One2many('rn.workflow.run', 'workflow_id')
    run_count = fields.Integer(compute='_compute_run_stats')
    success_rate = fields.Float(compute='_compute_run_stats', string='Success Rate %')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    ai_validation = fields.Text(string='AI Validation Notes', readonly=True)

    @api.depends('run_ids.state')
    def _compute_run_stats(self):
        for wf in self:
            runs = wf.run_ids
            wf.run_count = len(runs)
            done = runs.filtered(lambda r: r.state == 'done')
            wf.success_rate = round((len(done) / len(runs)) * 100.0, 1) if runs else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('trigger_type') == 'on_webhook' and not vals.get('webhook_token'):
                vals['webhook_token'] = self.env['ir.sequence'].next_by_code('rn.workflow.webhook') or ''
        return super().create(vals_list)

    def action_activate(self):
        for wf in self:
            notes = self.env['rn.workflow.ai.service'].validate_workflow(wf.id)
            wf.ai_validation = '\n'.join(notes) if notes else 'No issues detected.'
            wf.state = 'active'

    def action_pause(self):
        self.write({'state': 'paused'})

    def action_open_designer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_workflow_builder.designer',
            'name': self.name,
            'params': {'workflow_id': self.id},
        }

    def action_run_manual(self):
        self.ensure_one()
        return self.env['rn.workflow.engine'].run_workflow(self.id, trigger_payload={})
