# -*- coding: utf-8 -*-
"""REST API stubs for CRM Ultimate Pro."""

from odoo import http
from odoo.http import request


class RnCrmApiController(http.Controller):
    """JSON API placeholders for lead/dashboard/prediction/activity."""

    @http.route('/api/rn_crm/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return request.env['rn.crm.dashboard.service'].get_kpis()

    @http.route('/api/rn_crm/v1/predict', type='json', auth='user')
    def api_predict(self, lead_id=None, **kwargs):
        if not lead_id:
            return {'ok': False, 'error': 'lead_id required'}
        lead = request.env['crm.lead'].browse(int(lead_id)).exists()
        if not lead:
            return {'ok': False, 'error': 'Lead not found'}
        prediction = request.env['rn.crm.prediction.service'].predict(lead)
        return {'ok': True, 'prediction_id': prediction.id, 'win_probability': prediction.win_probability}

    @http.route('/api/rn_crm/v1/score', type='json', auth='user')
    def api_score(self, lead_id=None, **kwargs):
        if not lead_id:
            return {'ok': False, 'error': 'lead_id required'}
        lead = request.env['crm.lead'].browse(int(lead_id)).exists()
        if not lead:
            return {'ok': False, 'error': 'Lead not found'}
        request.env['rn.crm.lead.scoring.service'].recompute_scores(lead)
        return {'ok': True, 'score': lead.rn_lead_score, 'badge': lead.rn_score_badge}
