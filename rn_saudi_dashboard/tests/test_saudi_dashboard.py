# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_saudi_dashboard')
class TestRnSaudiDashboard(TransactionCase):

    def test_model_and_action_exist(self):
        self.assertIn('rn.saudi.dashboard', self.env)
        action = self.env.ref('rn_saudi_dashboard.action_rn_saudi_dashboard', raise_if_not_found=False)
        self.assertTrue(action)

    def test_dashboard_payload(self):
        data = self.env['rn.saudi.dashboard'].get_dashboard_data()
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(data)
