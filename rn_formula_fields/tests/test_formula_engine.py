# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..services.formula_engine import FormulaEngine


class TestFormulaEngine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.engine = FormulaEngine()

    def test_addition(self):
        self.assertEqual(self.engine.evaluate('price + cost', {'price': 10, 'cost': 4}), 14)

    def test_conditional_expression(self):
        self.assertEqual(self.engine.evaluate('amount * 2 if vip else amount', {'amount': 5, 'vip': True}), 10)

    def test_comparison_operators(self):
        self.assertTrue(self.engine.evaluate('amount >= 10 and amount <= 20', {'amount': 10}))

    def test_approved_function(self):
        self.assertEqual(self.engine.evaluate('round(price / 3, 2)', {'price': 10}), 3.33)

    def test_unknown_field_fails(self):
        with self.assertRaises(ValidationError):
            self.engine.evaluate('unknown + 1', {})

    def test_attribute_access_fails(self):
        with self.assertRaises(ValidationError):
            self.engine.evaluate('record.__class__', {'record': 1})

    def test_unapproved_function_fails(self):
        with self.assertRaises(ValidationError):
            self.engine.evaluate('__import__("os")', {})
