# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_payroll_portal_pro')
class TestRnPayrollPortalPro(TransactionCase):

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([('name', '=', 'rn_payroll_portal_pro')], limit=1)
        self.assertTrue(module)
        self.assertEqual(module.state, 'installed')

    def test_portal_templates_loaded(self):
        views = self.env['ir.ui.view'].search([
            ('key', 'ilike', 'rn_payroll_portal_pro%'),
        ], limit=5)
        self.assertTrue(views, 'Expected portal templates from rn_payroll_portal_pro')
