# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnWorkflowBuilder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_so = cls.env['ir.model'].search([('model', '=', 'sale.order')], limit=1)
        cls.workflow = cls.env['rn.workflow'].create({
            'name': 'Test SO Workflow',
            'trigger_type': 'on_create',
            'model_id': cls.model_so.id,
            'state': 'draft',
        })
        cls.env['rn.workflow.node'].create({
            'workflow_id': cls.workflow.id,
            'name': 'Notify team',
            'node_type': 'action',
            'action_type': 'send_notification',
            'config_json': '{"message": "SO created"}',
        })

    def test_ai_build_from_text(self):
        wf_id = self.env['rn.workflow.ai.service'].build_from_text(
            'When sales order above 5 lakh is confirmed, request approval and send email',
            model_name='sale.order',
        )
        wf = self.env['rn.workflow'].browse(wf_id)
        self.assertTrue(wf.node_ids)
        self.assertEqual(wf.model_name, 'sale.order')

    def test_ai_validate_workflow(self):
        notes = self.env['rn.workflow.ai.service'].validate_workflow(self.workflow.id)
        self.assertIsInstance(notes, list)

    def test_workflow_activation(self):
        self.workflow.action_activate()
        self.assertEqual(self.workflow.state, 'active')

    def test_manual_run(self):
        self.workflow.action_activate()
        run_id = self.env['rn.workflow.engine'].run_workflow(self.workflow.id)
        run = self.env['rn.workflow.run'].browse(run_id)
        self.assertEqual(run.state, 'done')
        self.assertTrue(run.log_ids)

    def test_condition_equals(self):
        partner = self.env['res.partner'].create({'name': 'WF Test'})
        product = self.env['product.product'].create({
            'name': 'WF Product',
            'list_price': 100,
        })
        so = self.env['sale.order'].with_context(rn_workflow_skip=True).create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 1})],
        })
        node = self.env['rn.workflow.node'].create({
            'workflow_id': self.workflow.id,
            'name': 'Check partner',
            'node_type': 'condition',
            'field_name': 'partner_id',
            'condition_operator': 'equals',
            'compare_value': str(partner.id),
        })
        passed = self.env['rn.workflow.condition.service'].evaluate(
            node,
            {'record_model': 'sale.order', 'record_id': so.id},
        )
        self.assertTrue(passed)

    def test_monitor_dashboard(self):
        data = self.env['rn.workflow.monitor.service'].get_dashboard_data()
        self.assertIn('active_workflows', data)
        self.assertIn('suggestions', data)

    def test_designer_payload(self):
        data = self.env['rn.workflow.engine'].get_designer_data(self.workflow.id)
        self.assertEqual(data['workflow']['id'], self.workflow.id)
        self.assertTrue(data['nodes'])

    def test_connector_data(self):
        connector = self.env.ref('rn_workflow_builder.connector_odoo')
        self.assertEqual(connector.connector_type, 'odoo')
