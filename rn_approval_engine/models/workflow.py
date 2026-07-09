# -*- coding: utf-8 -*-
"""Approval workflow template."""

from odoo import fields, models


class RnApprovalWorkflow(models.Model):
    """Reusable approval workflow bound to a document model."""

    _name = 'rn.approval.workflow'
    _description = 'Approval Workflow'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Html()
    model_id = fields.Many2one(
        'ir.model',
        string='Document Model',
        required=True,
        ondelete='cascade',
        domain=[('transient', '=', False)],
    )
    model_name = fields.Char(related='model_id.model', store=True)
    stage_ids = fields.One2many('rn.approval.workflow.stage', 'workflow_id', string='Stages')
    rule_ids = fields.One2many('rn.approval.rule', 'workflow_id', string='Rules')
    stage_count = fields.Integer(compute='_compute_stage_count')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _workflow_code_company_uniq = models.Constraint(
        'unique(code, company_id)',
        'Workflow code must be unique per company.',
    )

    def _compute_stage_count(self):
        for wf in self:
            wf.stage_count = len(wf.stage_ids)
