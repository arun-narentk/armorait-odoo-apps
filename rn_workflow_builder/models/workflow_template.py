# -*- coding: utf-8 -*-
"""Prebuilt workflow templates."""

from odoo import fields, models


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

    def action_create_workflow(self):
        self.ensure_one()
        wf = self.env['rn.workflow'].create({
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'trigger_type': self.trigger_type,
            'model_id': self.model_id.id,
            'state': 'draft',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.workflow',
            'res_id': wf.id,
            'view_mode': 'form',
            'target': 'current',
        }
