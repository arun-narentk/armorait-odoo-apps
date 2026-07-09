# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnApprovalEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_po = cls.env.ref('purchase.model_purchase_order')
        cls.approver_group = cls.env.ref('rn_approval_engine.group_rn_approval_approver')
        cls.manager_group = cls.env.ref('rn_approval_engine.group_rn_approval_manager')
        cls.workflow = cls.env['rn.approval.workflow'].create({
            'name': 'Test PO Workflow',
            'code': 'test_po',
            'model_id': cls.model_po.id,
            'company_id': cls.env.company.id,
        })
        cls.env['rn.approval.workflow.stage'].create({
            'workflow_id': cls.workflow.id,
            'name': 'Manager',
            'sequence': 10,
            'approver_type': 'group',
            'group_id': cls.approver_group.id,
        })
        cls.env['rn.approval.rule'].create({
            'name': 'Always PO',
            'workflow_id': cls.workflow.id,
            'rule_type': 'always',
        })
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Approval Test Vendor',
            'supplier_rank': 1,
        })

    def test_security_groups_exist(self):
        group = self.env.ref('rn_approval_engine.group_rn_approval_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_rule_service_finds_workflow(self):
        workflow = self.env['rn.approval.rule.service'].find_workflow(
            'purchase.order',
            amount=1000.0,
            company_id=self.env.company.id,
        )
        self.assertEqual(workflow, self.workflow)

    def test_submit_and_approve_flow(self):
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
        })
        po.order_line = [(0, 0, {
            'name': 'Test item',
            'product_qty': 1,
            'price_unit': 1000,
        })]
        request = self.env['rn.approval.request'].create({
            'workflow_id': self.workflow.id,
            'res_model': 'purchase.order',
            'res_id': po.id,
            'amount': po.amount_total,
            'company_id': self.env.company.id,
        })
        self.env['rn.approval.engine.service'].submit_request(request)
        self.assertEqual(request.state, 'pending')
        self.assertTrue(request.line_ids)
        line = request.line_ids.filtered(lambda l: l.is_active_stage)[:1]
        self.assertTrue(line)
        line.with_user(line.user_id).action_approve()
        self.assertEqual(request.state, 'approved')

    def test_risk_summary_new_vendor(self):
        po = self.env['purchase.order'].create({'partner_id': self.vendor.id})
        request = self.env['rn.approval.request'].create({
            'workflow_id': self.workflow.id,
            'res_model': 'purchase.order',
            'res_id': po.id,
            'amount': 10000,
            'company_id': self.env.company.id,
        })
        html = self.env['rn.approval.risk.service'].build_risk_summary(request)
        self.assertIn('New vendor', html)

    def test_dashboard_payload(self):
        data = self.env['rn.approval.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('pending', data['cards'])
