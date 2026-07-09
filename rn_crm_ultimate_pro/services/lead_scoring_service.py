# -*- coding: utf-8 -*-
"""Lead scoring engine."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmLeadScoringService(models.AbstractModel):
    """Apply score rules and keep lead scores between 0 and 100."""

    _name = 'rn.crm.lead.scoring.service'
    _description = 'CRM Lead Scoring Service'

    def recompute_scores(self, leads):
        """Recompute scores for leads using active rules."""
        rules = self.env['rn.crm.score.rule'].search([('active', '=', True)])
        History = self.env['rn.crm.score.history']
        for lead in leads:
            score = 0
            previous = lead.rn_lead_score or 0
            # Phase 2: evaluate each rule type against lead fields/domain.
            for rule in rules:
                if rule.rule_type == 'phone' and lead.phone:
                    score += rule.points
                elif rule.rule_type == 'email' and lead.email_from:
                    score += rule.points
                elif rule.rule_type == 'website' and lead.website:
                    score += rule.points
                elif rule.rule_type == 'revenue' and lead.expected_revenue:
                    score += rule.points
            score = max(0, min(100, score))
            lead.write({'rn_lead_score': score})
            History.create({
                'lead_id': lead.id,
                'score': score,
                'previous_score': previous,
                'note': 'Automated recompute',
            })
            _logger.info('Lead %s score %s -> %s', lead.id, previous, score)
        return True
