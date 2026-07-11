# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestFormulaSecurity(TransactionCase):
    def test_user_group_exists(self):
        self.assertTrue(self.env.ref('rn_formula_fields.group_rn_formula_user'))

    def test_manager_group_exists(self):
        manager = self.env.ref('rn_formula_fields.group_rn_formula_manager')
        user = self.env.ref('rn_formula_fields.group_rn_formula_user')
        self.assertIn(user, manager.implied_ids)

    def test_company_rules_exist(self):
        rules = self.env['ir.rule'].search([
            ('model_id.model', 'in', ['rn.formula.field', 'rn.formula.template']),
        ])
        self.assertGreaterEqual(len(rules), 1)
