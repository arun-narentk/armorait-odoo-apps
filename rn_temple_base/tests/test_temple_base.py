# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTempleBase(TransactionCase):
    """Phase 1 tests for ARMORA Temple Management Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_temple_base.group_rn_temple_counter', raise_if_not_found=False)
        self.assertTrue(group)

    def test_temple_sequence_and_branch(self):
        temple = self.env['rn.temple.temple'].create({
            'name': 'Test Temple',
            'institution_type': 'hindu_temple',
            'company_id': self.env.company.id,
        })
        self.assertNotEqual(temple.code, 'New')
        branch = self.env['rn.temple.branch'].create({
            'name': 'Main Branch',
            'temple_id': temple.id,
            'is_head_office': True,
        })
        self.assertTrue(branch.code)
        self.assertEqual(branch.company_id, self.env.company)

    def test_festival_workflow(self):
        temple = self.env['rn.temple.temple'].create({
            'name': 'Festival Temple',
            'company_id': self.env.company.id,
        })
        fest = self.env['rn.temple.festival'].create({
            'name': 'Test Utsavam',
            'temple_id': temple.id,
            'date_start': fields.Date.today(),
            'state': 'draft',
        })
        fest.action_confirm()
        self.assertEqual(fest.state, 'confirmed')

    def test_dashboard_and_upcoming_festivals(self):
        temple = self.env['rn.temple.temple'].create({
            'name': 'Dashboard Temple',
            'company_id': self.env.company.id,
        })
        self.env['rn.temple.festival'].create({
            'name': 'Soon Festival',
            'temple_id': temple.id,
            'date_start': fields.Date.today() + timedelta(days=10),
            'state': 'confirmed',
        })
        data = self.env['rn.temple.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertGreaterEqual(data['cards']['temples'], 1)
        upcoming = self.env['rn.temple.festival.service'].get_upcoming_festivals()
        self.assertTrue(any(f['name'] == 'Soon Festival' for f in upcoming))

    def test_settings_service(self):
        settings = self.env['rn.temple.temple.service'].ensure_default_settings()
        self.assertEqual(settings.company_id, self.env.company)
