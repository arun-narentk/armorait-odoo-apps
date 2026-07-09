# -*- coding: utf-8 -*-
"""Pick workflow from routing rules."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnApprovalRuleService(models.AbstractModel):
    """Evaluate rules and return matching workflow."""

    _name = 'rn.approval.rule.service'
    _description = 'Approval Rule Service'

    def find_workflow(self, res_model, amount=0.0, partner_id=False, department_id=False,
                      category_id=False, company_id=None):
        company_id = company_id or self.env.company.id
        Rule = self.env['rn.approval.rule']
        rules = Rule.search([
            ('active', '=', True),
            ('company_id', '=', company_id),
            ('model_id.model', '=', res_model),
        ], order='sequence, id')

        for rule in rules:
            if self._rule_matches(rule, amount, partner_id, department_id, category_id):
                return rule.workflow_id

        fallback = self.env['rn.approval.workflow'].search([
            ('model_name', '=', res_model),
            ('company_id', '=', company_id),
            ('active', '=', True),
        ], order='sequence', limit=1)
        return fallback

    def _rule_matches(self, rule, amount, partner_id, department_id, category_id):
        if rule.rule_type == 'always':
            return True
        if rule.rule_type == 'amount':
            if rule.amount_min and amount < rule.amount_min:
                return False
            if rule.amount_max and amount > rule.amount_max:
                return False
            return True
        if rule.rule_type == 'department':
            return bool(department_id and rule.department_id.id == department_id)
        if rule.rule_type == 'category':
            return bool(category_id and rule.category_id.id == category_id)
        if rule.rule_type == 'partner':
            return bool(partner_id and rule.partner_id.id == partner_id)
        return False
