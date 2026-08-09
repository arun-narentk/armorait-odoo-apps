# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_theme_base')
class TestRnThemeBase(TransactionCase):

    def test_module_installed(self):
        module = self.env['ir.module.module'].search([('name', '=', 'rn_theme_base')], limit=1)
        self.assertTrue(module)
        self.assertEqual(module.state, 'installed')

    def test_theme_utils_templates(self):
        utils = self.env['theme.utils']
        headers = utils._header_templates
        footers = utils._footer_templates
        self.assertTrue(any('rn_theme_base' in h for h in headers))
        self.assertTrue(any('rn_theme_base' in f for f in footers))
