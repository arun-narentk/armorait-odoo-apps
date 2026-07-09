# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_cloud_platform')
class TestCloudPlatform(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env.ref('rn_cloud_platform.provider_aws_default')
        cls.instance = cls.env['rn.cloud.instance'].create({
            'provider_id': cls.provider.id,
            'customer_name': 'ARMORA Demo',
            'domain_name': 'demo.armorait.cloud',
            'status': 'running',
        })
        cls.env['rn.cloud.environment'].create({
            'instance_id': cls.instance.id,
            'environment_type': 'production',
            'url': 'https://demo.armorait.cloud',
            'database_name': 'demo_cloud',
        })
        cls.env['rn.cloud.backup'].create({
            'instance_id': cls.instance.id,
            'backup_type': 'full',
            'size_mb': 512,
            'storage_location': 's3://backup/demo',
            'restore_state': 'unknown',
        })
        cls.env['rn.cloud.monitoring'].create({
            'instance_id': cls.instance.id,
            'cpu_percent': 91,
            'ram_percent': 78,
            'storage_percent': 82,
            'response_ms': 1450,
            'active_users': 25,
            'worker_utilization': 88,
        })
        cls.ops_service = cls.env['rn.cloud.ops.service']
        cls.dashboard_service = cls.env['rn.cloud.dashboard.service']

    def test_ops_analysis_creates_recommendations(self):
        recommendations = self.ops_service.analyze_instance(self.instance)
        self.assertTrue(recommendations)
        self.assertTrue(any(rec.category == 'performance' for rec in recommendations))

    def test_instance_counts_related_records(self):
        self.instance.invalidate_recordset(['backup_count', 'recommendation_count'])
        self.assertEqual(self.instance.backup_count, 1)

    def test_dashboard_returns_metrics(self):
        self.ops_service.analyze_instance(self.instance)
        data = self.dashboard_service.get_dashboard_data()
        self.assertIn('providers', data)
        self.assertIn('instances', data)
        self.assertIn('recent_recommendations', data)

    def test_provider_counts_instances(self):
        self.provider.invalidate_recordset(['instance_count'])
        self.assertGreaterEqual(self.provider.instance_count, 1)
