# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHrIntelligence(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env['rn.hr.intelligence.settings'].create({
            'name': 'Test HR Intel',
            'company_id': cls.env.company.id,
        })
        cls.department = cls.env['hr.department'].create({
            'name': 'Production',
            'company_id': cls.env.company.id,
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Worker',
            'department_id': cls.department.id,
            'company_id': cls.env.company.id,
        })
        cls.env['hr.version'].create({
            'name': 'Test Contract',
            'employee_id': cls.employee.id,
            'wage': 25000,
            'contract_date_start': fields.Date.today(),
            'date_version': fields.Date.today(),
            'company_id': cls.env.company.id,
        })

    def test_security_groups_exist(self):
        group = self.env.ref('rn_hr_intelligence.group_rn_hr_intel_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_executive_kpi(self):
        data = self.env['rn.hr.kpi.service'].get_executive_summary(self.env.company.id)
        self.assertGreaterEqual(data['headcount'], 1)
        self.assertGreater(data['gross_salary'], 0)

    def test_department_costs(self):
        costs = self.env['rn.hr.payroll.analytics.service'].get_department_costs(self.env.company.id)
        self.assertTrue(costs)
        self.assertEqual(costs[0]['department'], 'Production')

    def test_overtime_summary(self):
        self.env['rn.hr.overtime.log'].create({
            'name': 'OT-1',
            'employee_id': self.employee.id,
            'date': '2026-07-01',
            'hours': 4,
            'hourly_rate': 200,
            'company_id': self.env.company.id,
        })
        data = self.env['rn.hr.overtime.service'].get_overtime_summary(self.env.company.id)
        self.assertGreater(data['total_hours'], 0)

    def test_quality_checks(self):
        issues = self.env['rn.hr.quality.service'].run_quality_checks(self.env.company.id)
        self.assertIsInstance(issues, list)

    def test_ai_payroll_summary(self):
        insight = self.env['rn.hr.insight.service'].generate_payroll_summary(self.env.company.id)
        self.assertIn('payroll', insight.summary_html.lower())

    def test_dashboard_payload(self):
        data = self.env['rn.hr.dashboard.service'].get_dashboard_data(self.env.company.id)
        self.assertIn('executive', data)
        self.assertIn('departments', data)
