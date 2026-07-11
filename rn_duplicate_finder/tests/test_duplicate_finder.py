# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.rn_duplicate_finder.services.similarity_service import (
    compare_values,
    weighted_score,
)


@tagged('post_install', '-at_install')
class TestRnDuplicateFinder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule = cls.env['rn.dup.rule'].create({
            'name': 'Test Partner Rule',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'match_threshold': 80.0,
            'record_domain': "[('name', 'ilike', 'DUPTEST%')]",
            'field_line_ids': [
                (0, 0, {'field_name': 'email', 'match_type': 'exact', 'weight': 60}),
                (0, 0, {'field_name': 'name', 'match_type': 'fuzzy', 'weight': 40}),
            ],
        })
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'DUPTEST Alpha Contact',
            'email': 'dup.test@armorait.com',
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'DUPTEST Alpha Contact',
            'email': 'dup.test@armorait.com',
        })
        cls.partner_c = cls.env['res.partner'].create({
            'name': 'DUPTEST Different',
            'email': 'other@armorait.com',
        })

    def test_similarity_helpers(self):
        self.assertEqual(compare_values('Acme', 'acme', 'exact'), 100.0)
        self.assertGreater(compare_values('Acme Corp', 'Acme Corporation', 'fuzzy'), 50.0)
        self.assertEqual(compare_values('+91 98765 43210', '+91 98765 43210', 'phone'), 100.0)
        score = weighted_score([(100.0, 60.0), (80.0, 40.0)])
        self.assertAlmostEqual(score, 92.0)

    def test_partner_duplicate_scan(self):
        scan = self.env['rn.dup.scan.service'].run_rule_scan(self.rule)
        self.assertEqual(scan.state, 'done')
        self.assertGreaterEqual(scan.match_count, 1)
        result = scan.result_ids.filtered(
            lambda r: {r.res_id, r.duplicate_res_id} == {self.partner_a.id, self.partner_b.id}
        )
        self.assertTrue(result)
        self.assertGreaterEqual(result.score, 80.0)

    def test_ignore_pair_suppresses_future_matches(self):
        scan = self.env['rn.dup.scan.service'].run_rule_scan(self.rule)
        result = scan.result_ids.filtered(
            lambda r: {r.res_id, r.duplicate_res_id} == {self.partner_a.id, self.partner_b.id}
        )
        self.assertTrue(result)
        result.action_ignore_pair()
        scan2 = self.env['rn.dup.scan.service'].run_rule_scan(self.rule)
        blocked = scan2.result_ids.filtered(
            lambda r: {r.res_id, r.duplicate_res_id} == {self.partner_a.id, self.partner_b.id}
        )
        self.assertFalse(blocked)

    def test_merge_partners_archives_duplicate(self):
        dup = self.env['res.partner'].create({
            'name': 'DUPTEST Merge Target',
            'email': 'merge.target@armorait.com',
        })
        master = self.env['res.partner'].create({
            'name': 'DUPTEST Merge Master',
            'email': 'merge.target@armorait.com',
        })
        result = self.env['rn.dup.result'].create({
            'scan_id': self.env['rn.dup.scan'].create({
                'name': 'Merge Scan',
                'rule_id': self.rule.id,
                'state': 'done',
            }).id,
            'model_name': 'res.partner',
            'res_id': master.id,
            'duplicate_res_id': dup.id,
            'score': 95.0,
            'match_summary': 'email=100%',
        })
        self.env['rn.dup.merge.service'].merge_records(
            'res.partner', master.id, dup.id, result=result,
        )
        self.assertEqual(result.state, 'merged')
        self.assertFalse(dup.exists())
        self.assertTrue(master.exists())

    def test_security_groups_exist(self):
        group = self.env.ref('rn_duplicate_finder.group_rn_dup_finder_manager', raise_if_not_found=False)
        self.assertTrue(group)
