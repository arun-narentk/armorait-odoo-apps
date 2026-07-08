# -*- coding: utf-8 -*-
"""Pluggable prediction provider interface."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnCrmPredictionService(models.AbstractModel):
    """Predict win probability and next actions without binding to one AI vendor."""

    _name = 'rn.crm.prediction.service'
    _description = 'CRM Prediction Service'

    def predict(self, lead, provider='rule_engine'):
        """Create a prediction record for the lead."""
        lead.ensure_one()
        # Phase later: external providers implement the same method shape.
        win = lead.probability or 0.0
        if lead.rn_lead_score:
            win = max(win, float(lead.rn_lead_score))
        risk = 'low' if win >= 70 else 'medium' if win >= 40 else 'high'
        prediction = self.env['rn.crm.prediction'].create({
            'lead_id': lead.id,
            'win_probability': win,
            'expected_close_date': lead.date_deadline,
            'revenue_confidence': min(100.0, win),
            'recommended_activity': 'Schedule follow-up call',
            'risk_level': risk,
            'provider': provider,
        })
        lead.write({'rn_prediction_id': prediction.id, 'rn_risk_level': risk})
        _logger.info('Prediction created for lead %s provider=%s', lead.id, provider)
        return prediction
