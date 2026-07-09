# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_erp_health_analyzer')
class TestErpHealthAnalyzer(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.target = cls.env['rn.erp.health.target'].create({
            'name': 'Test Intelligence Scope',
            'target_type': 'database',
        })
        cls.scan_service = cls.env['rn.erp.health.scan.service']
        cls.dashboard_service = cls.env['rn.erp.health.dashboard.service']

    def test_run_scan_creates_scan_and_score(self):
        scan = self.scan_service.run_scan(self.target)
        self.assertEqual(scan.target_id, self.target)
        self.assertEqual(scan.state, 'done')
        self.assertGreaterEqual(scan.overall_score, 0)
        self.assertLessEqual(scan.overall_score, 100)

    def test_run_scan_creates_findings_or_clean_marker(self):
        scan = self.scan_service.run_scan(self.target)
        self.assertTrue(scan.finding_ids)
        self.assertTrue(scan.summary)

    def test_target_updates_after_scan(self):
        scan = self.scan_service.run_scan(self.target)
        self.target.invalidate_recordset(['last_scan_id', 'last_score'])
        self.assertEqual(self.target.last_scan_id, scan)
        self.assertEqual(self.target.last_score, scan.overall_score)

    def test_dashboard_service_returns_metrics(self):
        self.scan_service.run_scan(self.target)
        data = self.dashboard_service.get_dashboard_data()
        self.assertIn('latest_score', data)
        self.assertIn('recent_scans', data)
        self.assertIn('recent_findings', data)
