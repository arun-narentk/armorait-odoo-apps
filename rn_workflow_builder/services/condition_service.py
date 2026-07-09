# -*- coding: utf-8 -*-
"""Evaluate workflow condition nodes."""

import ast

from odoo import models


class RnWorkflowConditionService(models.AbstractModel):
    """Branch logic for workflow graphs."""

    _name = 'rn.workflow.condition.service'
    _description = 'Workflow Condition Service'

    def evaluate(self, node, context):
        record_model = context.get('record_model')
        record_id = context.get('record_id')
        if not record_model or not record_id:
            return bool(node.compare_value)

        record = self.env[record_model].browse(record_id)
        if not record.exists():
            return False

        if node.condition_operator == 'in_domain' and node.domain:
            try:
                domain = ast.literal_eval(node.domain)
                return bool(self.env[record_model].search_count(
                    domain + [('id', '=', record.id)]
                ))
            except (SyntaxError, ValueError):
                return False

        if not node.field_name or not hasattr(record, node.field_name):
            return False

        value = getattr(record, node.field_name)
        if hasattr(value, 'id'):
            value = value.id
        compare = node.compare_value or ''

        ops = {
            'equals': lambda a, b: str(a) == str(b),
            'not_equals': lambda a, b: str(a) != str(b),
            'greater': lambda a, b: float(a or 0) > float(b or 0),
            'less': lambda a, b: float(a or 0) < float(b or 0),
            'contains': lambda a, b: str(b).lower() in str(a).lower(),
        }
        func = ops.get(node.condition_operator, ops['equals'])
        return func(value, compare)
