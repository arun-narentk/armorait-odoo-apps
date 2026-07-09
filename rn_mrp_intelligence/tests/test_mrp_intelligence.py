# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnMrpIntelligence(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env['rn.mrp.intelligence.settings'].create({
            'name': 'Test Intel Settings',
            'company_id': cls.env.company.id,
        })
        cls.workcenter = cls.env['mrp.workcenter'].create({
            'name': 'Assembly Line 1',
            'company_id': cls.env.company.id,
        })
        cls.env['rn.mrp.workcenter.status'].create({
            'workcenter_id': cls.workcenter.id,
            'status': 'running',
            'queue_count': 2,
            'utilization_percent': 85.0,
            'company_id': cls.env.company.id,
        })

    def test_security_groups_exist(self):
        group = self.env.ref('rn_mrp_intelligence.group_rn_mrp_intel_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_executive_kpi_payload(self):
        data = self.env['rn.mrp.kpi.service'].get_executive_summary(self.env.company.id)
        self.assertIn('today_production_pct', data)
        self.assertIn('machine_utilization', data)

    def test_oee_computation(self):
        metrics = self.env['rn.mrp.oee.service'].compute_workcenter_oee(
            self.workcenter,
            company_id=self.env.company.id,
        )
        self.assertIn('oee', metrics)
        self.assertIn('availability', metrics)

    def test_bottleneck_detection(self):
        data = self.env['rn.mrp.bottleneck.service'].detect_bottlenecks(self.env.company.id)
        self.assertIn('workcenters', data)

    def test_ai_daily_summary(self):
        insight = self.env['rn.mrp.insight.service'].generate_daily_summary(self.env.company.id)
        self.assertTrue(insight.summary_html)
        self.assertEqual(insight.insight_type, 'daily_summary')

    def test_dashboard_payload(self):
        data = self.env['rn.mrp.dashboard.service'].get_dashboard_data(self.env.company.id)
        self.assertIn('executive', data)
        self.assertIn('workcenters', data)
