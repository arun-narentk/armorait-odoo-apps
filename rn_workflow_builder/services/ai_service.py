# -*- coding: utf-8 -*-
"""AI workflow builder, validation, and recommendations."""

import re

from odoo import fields, models


class RnWorkflowAiService(models.AbstractModel):
    """Heuristic AI: build workflows from text, validate graphs, suggest automations."""

    _name = 'rn.workflow.ai.service'
    _description = 'Workflow AI Service'

    def validate_workflow(self, workflow_id):
        workflow = self.env['rn.workflow'].browse(workflow_id)
        notes = []
        if not workflow.node_ids:
            notes.append('Warning: workflow has no nodes.')
        actions = workflow.node_ids.filtered(lambda n: n.node_type == 'action')
        if workflow.trigger_type in ('on_create', 'on_write') and not workflow.model_id:
            notes.append('Missing target model for record trigger.')
        if not actions:
            notes.append('No action nodes defined.')
        if len(workflow.node_ids) > 50:
            notes.append('Large workflow: consider splitting for maintainability.')
        parent_map = {n.parent_id.id: n.id for n in workflow.node_ids if n.parent_id}
        if len(parent_map) != len(set(parent_map.values())):
            notes.append('Possible loop detected in node parent chain.')
        return notes

    def build_from_text(self, prompt, model_name=None):
        """Parse plain-English prompt into draft workflow nodes (heuristic)."""
        prompt_lower = (prompt or '').lower()
        trigger_type = 'on_write'
        if 'confirmed' in prompt_lower or 'created' in prompt_lower:
            trigger_type = 'on_create' if 'created' in prompt_lower else 'on_write'

        if not model_name:
            if 'sales order' in prompt_lower or 'quotation' in prompt_lower:
                model_name = 'sale.order'
            elif 'purchase' in prompt_lower or 'rfq' in prompt_lower:
                model_name = 'purchase.order'
            elif 'invoice' in prompt_lower or 'bill' in prompt_lower:
                model_name = 'account.move'

        model = self.env['ir.model'].search([('model', '=', model_name)], limit=1) if model_name else False
        amount_match = re.search(r'([\d,.]+)\s*(lakh|lac|crore|₹|rs)?', prompt_lower)
        compare_value = ''
        if amount_match:
            compare_value = amount_match.group(1).replace(',', '')

        workflow_vals = {
            'name': 'AI Draft Workflow',
            'description': prompt,
            'trigger_type': trigger_type,
            'model_id': model.id if model else False,
            'state': 'draft',
        }
        workflow = self.env['rn.workflow'].create(workflow_vals)

        seq = 10
        nodes = []
        if compare_value:
            nodes.append({
                'workflow_id': workflow.id,
                'name': 'Check amount threshold',
                'sequence': seq,
                'node_type': 'condition',
                'field_name': 'amount_total',
                'condition_operator': 'greater',
                'compare_value': compare_value,
            })
            seq += 10
        if 'approval' in prompt_lower or 'approve' in prompt_lower:
            nodes.append({
                'workflow_id': workflow.id,
                'name': 'Request finance approval',
                'sequence': seq,
                'node_type': 'action',
                'action_type': 'start_approval',
            })
            seq += 10
        if 'invoice' in prompt_lower:
            nodes.append({
                'workflow_id': workflow.id,
                'name': 'Generate invoice',
                'sequence': seq,
                'node_type': 'action',
                'action_type': 'update_record',
                'config_json': '{"values": {"invoice_status": "to invoice"}}',
            })
            seq += 10
        if 'whatsapp' in prompt_lower or 'notify' in prompt_lower or 'email' in prompt_lower:
            nodes.append({
                'workflow_id': workflow.id,
                'name': 'Send notification',
                'sequence': seq,
                'node_type': 'action',
                'action_type': 'send_email',
                'config_json': '{"subject": "Workflow notification", "body": "<p>Automated step completed.</p>"}',
            })
            seq += 10

        if not nodes:
            nodes.append({
                'workflow_id': workflow.id,
                'name': 'Log workflow event',
                'sequence': seq,
                'node_type': 'action',
                'action_type': 'send_notification',
                'config_json': '{"message": "Workflow triggered."}',
            })

        self.env['rn.workflow.node'].create(nodes)
        workflow.ai_validation = '\n'.join(self.validate_workflow(workflow.id))
        return workflow.id

    def suggest_automations(self, company_id=None):
        company_id = company_id or self.env.company.id
        suggestions = []
        so_count = self.env['sale.order'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'sale'),
        ])
        if so_count > 5:
            suggestions.append(
                'You confirm sales orders often. Automate project or invoice creation after confirmation.'
            )
        overdue = self.env['account.move'].search_count([
            ('company_id', '=', company_id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ])
        if overdue > 3:
            suggestions.append(
                'Several invoices are unpaid. Schedule overdue reminder emails every Friday.'
            )
        if not suggestions:
            suggestions.append('No patterns detected yet. Connect more workflows to enable suggestions.')
        return suggestions

    def summarize_context(self, context):
        model = context.get('record_model', '')
        res_id = context.get('record_id', 0)
        payload = context.get('payload', {})
        name = payload.get('display_name', '')
        return (
            f'Workflow summary at {fields.Datetime.to_string(fields.Datetime.now())}: '
            f'{model} #{res_id} {name}. Automated step completed.'
        )
