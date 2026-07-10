# -*- coding: utf-8 -*-
"""Prebuilt workflow templates."""

import json
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

_TEMPLATE_NODE_FIELDS = {
    'name',
    'sequence',
    'node_type',
    'action_type',
    'condition_operator',
    'field_name',
    'compare_value',
    'domain',
    'target_model_id',
    'config_json',
    'connector_id',
}


class RnWorkflowTemplate(models.Model):
    """Marketplace-ready workflow starter templates."""

    _name = 'rn.workflow.template'
    _description = 'Workflow Template'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    description = fields.Text()
    category = fields.Selection(
        [
            ('sales', 'Sales'),
            ('purchase', 'Purchase'),
            ('inventory', 'Inventory'),
            ('accounting', 'Accounting'),
            ('hr', 'HR'),
            ('crm', 'CRM'),
            ('manufacturing', 'Manufacturing'),
            ('general', 'General'),
        ],
        default='general',
    )
    trigger_type = fields.Selection(
        [
            ('on_create', 'Record Created'),
            ('on_write', 'Record Updated'),
            ('on_schedule', 'Scheduled'),
            ('on_webhook', 'Webhook'),
        ],
        default='on_create',
    )
    model_id = fields.Many2one('ir.model', string='Target Model')
    template_json = fields.Text(string='Node Template JSON')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    def _prepare_workflow_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'trigger_type': self.trigger_type,
            'model_id': self.model_id.id,
            'state': 'draft',
        }

    def _create_nodes_from_template(self, workflow):
        self.ensure_one()
        if not self.template_json:
            return
        try:
            nodes_data = json.loads(self.template_json)
        except json.JSONDecodeError:
            _logger.warning('Invalid template_json on workflow template %s', self.code)
            return
        if not isinstance(nodes_data, list):
            return

        Node = self.env['rn.workflow.node']
        for node_vals in nodes_data:
            if not isinstance(node_vals, dict):
                continue
            vals = {
                key: node_vals[key]
                for key in _TEMPLATE_NODE_FIELDS
                if key in node_vals
            }
            vals['workflow_id'] = workflow.id
            if vals.get('target_model_id'):
                vals['target_model_id'] = int(vals['target_model_id'])
            if vals.get('connector_id'):
                vals['connector_id'] = int(vals['connector_id'])
            Node.create(vals)

    def create_workflow_from_template(self):
        """Instantiate a draft workflow with template nodes."""
        self.ensure_one()
        workflow = self.env['rn.workflow'].create(self._prepare_workflow_vals())
        self._create_nodes_from_template(workflow)
        return workflow

    def action_create_workflow(self):
        self.ensure_one()
        workflow = self.create_workflow_from_template()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.workflow',
            'res_id': workflow.id,
            'view_mode': 'form',
            'target': 'current',
        }
