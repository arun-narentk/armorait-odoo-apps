# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnRealestateBase(TransactionCase):
    """Phase 1 tests for ARMORA Real Estate ERP Core."""

    def setUp(self):
        super().setUp()
        self.developer = self.env['rn.realestate.developer'].create({
            'name': 'Test Builder',
            'company_id': self.env.company.id,
        })
        self.project = self.env['rn.realestate.project'].create({
            'name': 'Test Project',
            'developer_id': self.developer.id,
            'project_type': 'apartment',
        })

    def test_groups_exist(self):
        group = self.env.ref('rn_realestate_base.group_rn_realestate_sales', raise_if_not_found=False)
        self.assertTrue(group)

    def test_developer_project_sequences(self):
        self.assertNotEqual(self.developer.code, 'New')
        self.assertNotEqual(self.project.code, 'New')

    def test_unit_status_workflow(self):
        unit = self.env['rn.realestate.unit'].create({
            'name': 'T-101',
            'developer_id': self.developer.id,
            'project_id': self.project.id,
            'unit_type': 'apartment',
            'status': 'available',
        })
        self.assertNotEqual(unit.code, 'New')
        unit.action_block()
        self.assertEqual(unit.status, 'blocked')
        unit.action_mark_booked()
        self.assertEqual(unit.status, 'booked')

    def test_lead_pipeline(self):
        lead = self.env['rn.realestate.lead'].create({
            'name': 'Test Lead',
            'developer_id': self.developer.id,
            'lead_source': 'walkin',
            'stage': 'new',
        })
        self.assertNotEqual(lead.reference, 'New')
        lead.action_contact()
        self.assertEqual(lead.stage, 'contacted')

    def test_dashboard_and_inventory(self):
        self.env['rn.realestate.unit'].create({
            'name': 'T-102',
            'developer_id': self.developer.id,
            'project_id': self.project.id,
            'unit_type': 'apartment',
            'status': 'available',
        })
        data = self.env['rn.realestate.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertGreaterEqual(data['cards']['available_units'], 1)
        inv = self.env['rn.realestate.developer.service'].get_inventory_summary()
        self.assertGreaterEqual(inv['total'], 1)

    def test_settings_service(self):
        settings = self.env['rn.realestate.developer.service'].ensure_default_settings()
        self.assertEqual(settings.company_id, self.env.company)
