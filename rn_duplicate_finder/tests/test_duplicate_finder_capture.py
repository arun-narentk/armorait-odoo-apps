# -*- coding: utf-8 -*-
"""Tests for demo data and menu actions used in live Apps Store captures."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'rn_duplicate_finder_capture')
class TestRnDuplicateFinderCaptureData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule = cls.env['rn.dup.rule'].create({
            'name': 'DUPCAP Capture Rule',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'match_threshold': 80.0,
            'record_domain': "[('name', 'ilike', 'DUPCAP%')]",
            'field_line_ids': [
                (0, 0, {'field_name': 'email', 'match_type': 'exact', 'weight': 60}),
                (0, 0, {'field_name': 'name', 'match_type': 'fuzzy', 'weight': 40}),
            ],
        })
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'DUPCAP Demo Alpha',
            'email': 'dupcap.demo@armorait.com',
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'DUPCAP Demo Alpha',
            'email': 'dupcap.demo@armorait.com',
        })

    def test_capture_rule_scan_produces_matches(self):
        scan = self.env['rn.dup.scan.service'].run_rule_scan(self.rule)
        self.assertEqual(scan.state, 'done')
        self.assertGreaterEqual(scan.match_count, 1)
        result = scan.result_ids.filtered(
            lambda r: {r.res_id, r.duplicate_res_id} == {self.partner_a.id, self.partner_b.id}
        )
        self.assertTrue(result)
        self.assertGreaterEqual(result.score, 80.0)
        self.assertEqual(result.state, 'new')

    def test_matches_window_action_exists(self):
        action = self.env.ref('rn_duplicate_finder.action_rn_dup_result', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.dup.result')
        self.assertIn('list', action.view_mode)

    def test_rules_window_action_exists(self):
        action = self.env.ref('rn_duplicate_finder.action_rn_dup_rule', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.dup.rule')

    def test_scans_window_action_exists(self):
        action = self.env.ref('rn_duplicate_finder.action_rn_dup_scan', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.dup.scan')

    def test_ignore_window_action_exists(self):
        action = self.env.ref('rn_duplicate_finder.action_rn_dup_ignore', raise_if_not_found=False)
        self.assertTrue(action)
        self.assertEqual(action.res_model, 'rn.dup.ignore')

    def test_demo_xml_partners_available(self):
        partners = self.env['res.partner'].search([('name', 'ilike', 'DUPCAP%')])
        self.assertGreaterEqual(len(partners), 2)

    def test_merge_wizard_action_on_result(self):
        scan = self.env['rn.dup.scan.service'].run_rule_scan(self.rule)
        result = scan.result_ids[:1]
        self.assertTrue(result)
        action = result.action_open_merge_wizard()
        self.assertEqual(action['res_model'], 'rn.dup.merge.wizard')
        self.assertEqual(action['target'], 'new')
