# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFormulaField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env.ref('product.model_product_template')
        cls.Formula = cls.env['rn.formula.field']

    def _values(self, **extra):
        values = {
            'name': 'Test Margin',
            'model_id': self.model.id,
            'field_name': 'x_rn_formula_test_margin',
            'expression': 'list_price - standard_price',
            'field_dependencies': 'list_price,standard_price',
        }
        values.update(extra)
        return values

    def test_create_syncs_ir_field(self):
        formula = self.Formula.create(self._values())
        self.assertTrue(formula.ir_field_id)
        self.assertIn("self.env['rn.formula.field']", formula.ir_field_id.compute)

    def test_compute_code_contains_field_name(self):
        formula = self.Formula.create(self._values(field_name='x_rn_formula_compute_code'))
        self.assertIn("record['x_rn_formula_compute_code']", formula._compute_code())

    def test_invalid_technical_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.Formula.create(self._values(field_name='margin'))

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.Formula.create(self._values(
                field_name='x_rn_formula_invalid_dependency',
                field_dependencies='missing_field'))

    def test_formula_evaluates_record(self):
        formula = self.Formula.create(self._values(field_name='x_rn_formula_evaluate'))
        product = self.env['product.template'].create({
            'name': 'Formula Test Product', 'list_price': 25, 'standard_price': 10,
        })
        self.assertEqual(formula._engine.evaluate_record(formula, product), 15)

    def test_expression_update_resyncs_field(self):
        formula = self.Formula.create(self._values(field_name='x_rn_formula_resync'))
        formula.write({'expression': 'list_price * 2'})
        self.assertIn("record['x_rn_formula_resync']", formula.ir_field_id.compute)
