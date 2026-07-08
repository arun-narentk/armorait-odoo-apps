# -*- coding: utf-8 -*-
"""CRM lead extensions for Ultimate Pro."""

from odoo import api, fields, models


class CrmLead(models.Model):
    """Extend leads with score, risk, and enrichment placeholders."""

    _inherit = 'crm.lead'

    rn_lead_score = fields.Integer(string='Lead Score', tracking=True, index=True)
    rn_score_badge = fields.Selection(
        selection=[
            ('cold', 'Cold'),
            ('warm', 'Warm'),
            ('hot', 'Hot'),
            ('priority', 'Priority'),
        ],
        compute='_compute_rn_score_badge',
        store=True,
    )
    rn_risk_level = fields.Selection(
        selection=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        string='Risk Level',
    )
    rn_stage_entered_at = fields.Datetime(string='Stage Entered At')
    rn_stage_age_days = fields.Integer(compute='_compute_rn_stage_age_days')
    rn_prediction_id = fields.Many2one('rn.crm.prediction', string='Latest Prediction')
    rn_enriched = fields.Boolean(string='Enriched')
    rn_score_history_ids = fields.One2many('rn.crm.score.history', 'lead_id', string='Score History')

    @api.depends('rn_lead_score')
    def _compute_rn_score_badge(self):
        for lead in self:
            score = lead.rn_lead_score or 0
            if score >= 80:
                lead.rn_score_badge = 'priority'
            elif score >= 60:
                lead.rn_score_badge = 'hot'
            elif score >= 30:
                lead.rn_score_badge = 'warm'
            else:
                lead.rn_score_badge = 'cold'

    def _compute_rn_stage_age_days(self):
        now = fields.Datetime.now()
        for lead in self:
            if lead.rn_stage_entered_at:
                delta = now - lead.rn_stage_entered_at
                lead.rn_stage_age_days = delta.days
            else:
                lead.rn_stage_age_days = 0

    def action_rn_recompute_score(self):
        """Recompute lead score via scoring service."""
        self.env['rn.crm.lead.scoring.service'].recompute_scores(self)
        return True

    def action_rn_detect_duplicates(self):
        """Find duplicates for this lead."""
        self.env['rn.crm.duplicate.service'].scan_leads(self)
        return True
