# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnConstructionCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['rn.construction.project'].create({
            'name': 'Test Tower',
            'code': 'TT-01',
            'date_start': '2026-01-01',
            'date_end': '2026-12-31',
            'budget_total': 1000000,
            'state': 'active',
        })
        cls.site = cls.env['rn.construction.site'].create({
            'name': 'Site 1',
            'construction_project_id': cls.project.id,
        })

    def test_boq_revision(self):
        boq = self.env['rn.construction.boq'].create({
            'name': 'BOQ v1',
            'construction_project_id': self.project.id,
            'line_ids': [(0, 0, {
                'description': 'Steel',
                'item_type': 'material',
                'quantity': 10,
                'unit_rate': 5000,
            })],
        })
        new_id = self.env['rn.construction.boq.service'].create_revision(boq.id)
        new_boq = self.env['rn.construction.boq'].browse(new_id)
        self.assertEqual(new_boq.version, 2)
        self.assertEqual(boq.state, 'revised')

    def test_estimation_from_boq(self):
        boq = self.env['rn.construction.boq'].create({
            'name': 'BOQ Est',
            'construction_project_id': self.project.id,
            'line_ids': [
                (0, 0, {'description': 'Cement', 'item_type': 'material', 'quantity': 100, 'unit_rate': 400}),
                (0, 0, {'description': 'Labour', 'item_type': 'labour', 'quantity': 50, 'unit_rate': 800}),
            ],
        })
        est_id = self.env['rn.construction.estimation.service'].build_from_boq(boq.id)
        est = self.env['rn.construction.cost.estimate'].browse(est_id)
        self.assertEqual(est.material_cost, 40000)
        self.assertEqual(est.labour_cost, 40000)

    def test_material_request_flow(self):
        product = self.env['product.product'].create({'name': 'Cement Bag', 'type': 'consu'})
        req = self.env['rn.construction.material.request'].create({
            'site_id': self.site.id,
            'product_id': product.id,
            'quantity': 50,
        })
        self.env['rn.construction.procurement.service'].submit_material_request(req.id)
        self.assertEqual(req.state, 'submitted')
        self.env['rn.construction.procurement.service'].approve_material_request(req.id)
        self.assertEqual(req.state, 'approved')

    def test_running_bill_retention(self):
        bill = self.env['rn.construction.running.bill'].create({
            'construction_project_id': self.project.id,
            'work_done_amount': 100000,
            'retention_pct': 10,
        })
        self.assertEqual(bill.retention_amount, 10000)
        self.assertEqual(bill.net_payable, 90000)

    def test_ai_insights(self):
        answer = self.env['rn.construction.insight.service'].answer_project_question(
            'Is project behind schedule?',
            project_id=self.project.id,
        )
        self.assertTrue(answer)
        risk = self.env['rn.construction.insight.service'].predict_cost_risk(self.project.id)
        self.assertIn(risk['risk_level'], ('low', 'medium', 'high'))

    def test_dashboard(self):
        data = self.env['rn.construction.dashboard.service'].get_management_dashboard()
        self.assertIn('active_projects', data)
        site_data = self.env['rn.construction.dashboard.service'].get_site_engineer_dashboard()
        self.assertIn('site_count', site_data)
