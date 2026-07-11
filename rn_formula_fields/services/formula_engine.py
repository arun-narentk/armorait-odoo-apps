# -*- coding: utf-8 -*-
"""Safe formula parsing and evaluation for configurable formula fields."""

import ast
import math
import operator
from decimal import Decimal
from typing import Any

from odoo.exceptions import ValidationError


class FormulaEngine:
    """Evaluate a deliberately small arithmetic expression language."""

    _BINARY_OPERATORS = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
    }
    _UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    _COMPARISON_OPERATORS = {
        ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
        ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
    }
    _FUNCTIONS = {
        'abs': abs, 'ceil': math.ceil, 'floor': math.floor, 'max': max,
        'min': min, 'round': round,
    }
    _ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp,
        ast.And, ast.Or, ast.IfExp, ast.Name, ast.Load, ast.Constant,
        ast.Call, ast.keyword,
    )

    def validate(self, expression: str) -> ast.Expression:
        if not expression or not expression.strip():
            raise ValidationError("A formula expression is required.")
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as error:
            raise ValidationError("Invalid formula syntax: %s" % error.msg) from error
        for node in ast.walk(tree):
            if isinstance(node, (ast.operator, ast.cmpop)):
                continue
            if not isinstance(node, self._ALLOWED_NODES):
                raise ValidationError("Formula element '%s' is not allowed." % type(node).__name__)
            if isinstance(node, ast.BinOp) and type(node.op) not in self._BINARY_OPERATORS:
                raise ValidationError("This arithmetic operator is not allowed.")
            if isinstance(node, ast.UnaryOp) and type(node.op) not in self._UNARY_OPERATORS:
                raise ValidationError("This unary operator is not allowed.")
            if isinstance(node, ast.Compare) and any(
                    type(op) not in self._COMPARISON_OPERATORS for op in node.ops):
                raise ValidationError("This comparison operator is not allowed.")
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in self._FUNCTIONS:
                    raise ValidationError("Only approved formula functions may be called.")
                if node.keywords:
                    raise ValidationError("Formula functions do not accept keyword arguments.")
            if isinstance(node, ast.Name) and node.id.startswith('_'):
                raise ValidationError("Private names are not allowed in formulas.")
        return tree

    def evaluate(self, expression: str, values: dict[str, Any]) -> Any:
        return self._evaluate_node(self.validate(expression).body, values)

    def evaluate_record(self, formula: Any, record: Any) -> Any:
        field_names = formula._dependency_names()
        values = {
            field_name: self._normalise_value(record[field_name])
            for field_name in field_names if field_name in record._fields
        }
        return self.evaluate(formula.expression, values)

    def _extract_names(self, expression: str) -> list[str]:
        return sorted({
            node.id for node in ast.walk(self.validate(expression))
            if isinstance(node, ast.Name) and node.id not in self._FUNCTIONS
        })

    @staticmethod
    def _normalise_value(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, 'ids'):
            return value.id if len(value) == 1 else len(value)
        return value or 0

    def _evaluate_node(self, node: ast.AST, values: dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, bool)):
                return node.value
            raise ValidationError("Only numeric constants are allowed.")
        if isinstance(node, ast.Name):
            if node.id not in values:
                raise ValidationError("Unknown formula field '%s'." % node.id)
            return values[node.id]
        if isinstance(node, ast.BinOp):
            return self._BINARY_OPERATORS[type(node.op)](
                self._evaluate_node(node.left, values), self._evaluate_node(node.right, values))
        if isinstance(node, ast.UnaryOp):
            return self._UNARY_OPERATORS[type(node.op)](self._evaluate_node(node.operand, values))
        if isinstance(node, ast.BoolOp):
            evaluated = [self._evaluate_node(item, values) for item in node.values]
            return all(evaluated) if isinstance(node.op, ast.And) else any(evaluated)
        if isinstance(node, ast.Compare):
            left = self._evaluate_node(node.left, values)
            for operation, comparator in zip(node.ops, node.comparators):
                right = self._evaluate_node(comparator, values)
                if not self._COMPARISON_OPERATORS[type(operation)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.IfExp):
            branch = node.body if self._evaluate_node(node.test, values) else node.orelse
            return self._evaluate_node(branch, values)
        if isinstance(node, ast.Call):
            return self._FUNCTIONS[node.func.id](*[
                self._evaluate_node(argument, values) for argument in node.args
            ])
        raise ValidationError("Unsupported formula expression.")
