# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnCrmUltimateSkeleton(TransactionCase):
    """Phase 1 tests for CRM Ultimate Pro."""

    def test_groups_exist(self):
        group = self.env.ref('rn_crm_ultimate_pro.group_rn_crm_salesperson', raise_if_not_found=False)
        self.assertTrue(group)

    def test_score_recompute(self):
        lead = self.env['crm.lead'].create({
            'name': 'Score Test Lead',
            'type': 'lead',
            'email_from': 'buyer@example.com',
            'phone': '+15550001111',
            'website': 'https://example.com',
            'expected_revenue': 10000,
        })
        self.env['rn.crm.lead.scoring.service'].recompute_scores(lead)
        self.assertGreater(lead.rn_lead_score, 0)
        self.assertTrue(lead.rn_score_badge)

    def test_duplicate_email_scan(self):
        self.env['crm.lead'].create({
            'name': 'Dup A',
            'type': 'lead',
            'email_from': 'dup@example.com',
        })
        self.env['crm.lead'].create({
            'name': 'Dup B',
            'type': 'lead',
            'email_from': 'dup@example.com',
        })
        batch = self.env['rn.crm.duplicate.service'].scan_leads()
        self.assertEqual(batch.state, 'done')
        self.assertGreaterEqual(batch.match_count, 1)

    def test_prediction_rule_engine(self):
        lead = self.env['crm.lead'].create({
            'name': 'Predict Lead',
            'type': 'opportunity',
            'probability': 55,
            'rn_lead_score': 70,
        })
        prediction = self.env['rn.crm.prediction.service'].predict(lead)
        self.assertTrue(prediction.id)
        self.assertEqual(lead.rn_prediction_id, prediction)
