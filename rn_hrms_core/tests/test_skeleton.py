# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHrmsCoreSkeleton(TransactionCase):
    """Phase 1 tests for ARMORA HRMS Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_hrms_core.group_rn_hrms_officer', raise_if_not_found=False)
        self.assertTrue(group)

    def test_dashboard_payload(self):
        data = self.env['rn.hrms.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertIn('employee_count', data['cards'])

    def test_onboard_and_approval(self):
        employee = self.env['hr.employee'].create({'name': 'HRMS Test Employee'})
        self.env['rn.hrms.onboarding.service'].onboard_employee(employee)
        self.assertTrue(employee.rn_hrms_employee_code)
        self.assertTrue(employee.rn_hrms_onboarded)
        approval = self.env['rn.hrms.approval'].create({
            'request_type': 'general',
            'employee_id': employee.id,
            'summary': 'Test approval',
        })
        self.env['rn.hrms.approval.service'].submit(approval)
        self.assertEqual(approval.state, 'pending')
        self.env['rn.hrms.approval.service'].approve(approval)
        self.assertEqual(approval.state, 'approved')
