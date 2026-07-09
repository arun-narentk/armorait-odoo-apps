# -*- coding: utf-8 -*-
"""Workflow graph nodes."""

from odoo import fields, models


class RnWorkflowNode(models.Model):
    """Single step: trigger, condition, or action."""

    _name = 'rn.workflow.node'
    _description = 'Workflow Node'
    _order = 'sequence, id'

    workflow_id = fields.Many2one('rn.workflow', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    node_type = fields.Selection(
        [
            ('trigger', 'Trigger'),
            ('condition', 'Condition'),
            ('action', 'Action'),
        ],
        required=True,
        default='action',
    )
    connector_id = fields.Many2one('rn.workflow.connector', string='Connector')
    action_type = fields.Selection(
        [
            ('create_record', 'Create Record'),
            ('update_record', 'Update Record'),
            ('send_email', 'Send Email'),
            ('send_notification', 'Send Notification'),
            ('call_webhook', 'Call Webhook'),
            ('start_approval', 'Start Approval'),
            ('python_code', 'Execute Python (sandboxed)'),
            ('ai_summary', 'Generate AI Summary'),
        ],
    )
    condition_operator = fields.Selection(
        [
            ('equals', 'Equals'),
            ('not_equals', 'Not Equals'),
            ('greater', 'Greater Than'),
            ('less', 'Less Than'),
            ('contains', 'Contains'),
            ('in_domain', 'Matches Domain'),
        ],
        default='equals',
    )
    field_name = fields.Char(string='Field')
    compare_value = fields.Char(string='Compare Value')
    domain = fields.Char(string='Domain Expression')
    target_model_id = fields.Many2one('ir.model', string='Action Model')
    target_model_name = fields.Char(related='target_model_id.model', store=True)
    config_json = fields.Text(string='Configuration JSON')
    parent_id = fields.Many2one('rn.workflow.node', string='Parent Node', ondelete='set null')
    branch_true_id = fields.Many2one('rn.workflow.node', string='If True', ondelete='set null')
    branch_false_id = fields.Many2one('rn.workflow.node', string='If False', ondelete='set null')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        related='workflow_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
