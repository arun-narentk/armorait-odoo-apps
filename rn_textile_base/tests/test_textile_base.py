# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTextileBase(TransactionCase):
    """Phase 1 tests for ARMORA Textile Manufacturing Core."""

    def setUp(self):
        super().setUp()
        self.factory = self.env['rn.textile.factory'].create({
            'name': 'Test Knitting Unit',
            'unit_type': 'knitting',
            'company_id': self.env.company.id,
        })
        self.department = self.env['rn.textile.department'].create({
            'name': 'Knitting',
            'factory_id': self.factory.id,
            'department_type': 'knitting',
        })

    def test_groups_exist(self):
        group = self.env.ref('rn_textile_base.group_rn_textile_operator', raise_if_not_found=False)
        self.assertTrue(group)

    def test_factory_and_machine_sequences(self):
        self.assertNotEqual(self.factory.code, 'New')
        machine = self.env['rn.textile.machine'].create({
            'name': 'Knitter 1',
            'factory_id': self.factory.id,
            'department_id': self.department.id,
            'machine_type': 'knitting',
        })
        self.assertNotEqual(machine.code, 'New')
        self.assertEqual(machine.company_id, self.env.company)

    def test_yarn_spec_sequence(self):
        spec = self.env['rn.textile.yarn.spec'].create({
            'name': '24s Combed',
            'factory_id': self.factory.id,
            'yarn_count': '24s',
            'blend_type': 'cotton',
        })
        self.assertNotEqual(spec.code, 'New')

    def test_dashboard_and_utilization(self):
        self.env['rn.textile.machine'].create({
            'name': 'Active Machine',
            'factory_id': self.factory.id,
            'department_id': self.department.id,
            'machine_type': 'knitting',
            'state': 'active',
        })
        data = self.env['rn.textile.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertGreaterEqual(data['cards']['factories'], 1)
        util = self.env['rn.textile.factory.service'].get_machine_utilization_summary()
        self.assertGreaterEqual(util['total'], 1)

    def test_settings_service(self):
        settings = self.env['rn.textile.factory.service'].ensure_default_settings()
        self.assertEqual(settings.company_id, self.env.company)
