# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnAiSiteBase(TransactionCase):
    """Phase 1 tests for ARMORA AI Business Launch Core."""

    def test_groups_exist(self):
        group = self.env.ref('rn_ai_site_base.group_rn_ai_site_user', raise_if_not_found=False)
        self.assertTrue(group)

    def test_brief_analyze_extracts_keywords(self):
        brief = self.env['rn.ai.site.brief'].create({
            'name': 'Test Brief',
            'business_name': 'Sweet Cakes Coimbatore',
            'business_type': 'bakery',
            'location': 'Coimbatore',
            'description': 'Custom wedding cakes and birthday cakes with delivery.',
            'company_id': self.env.company.id,
        })
        brief.action_analyze()
        self.assertEqual(brief.state, 'analyzed')
        self.assertTrue(brief.keywords)
        self.assertIn('Coimbatore', brief.keywords)

    def test_generate_site_from_brief(self):
        brief = self.env['rn.ai.site.brief'].create({
            'name': 'Gym Launch',
            'business_name': 'FitZone Gym',
            'business_type': 'gym',
            'location': 'Coimbatore',
            'description': 'Personal training and group fitness classes.',
            'services': 'Personal training, Yoga, Zumba',
            'company_id': self.env.company.id,
        })
        brief.action_generate_site()
        self.assertTrue(brief.site_id)
        self.assertGreater(brief.site_id.page_count, 5)
        home = brief.site_id.page_ids.filtered(lambda p: p.page_type == 'home')
        self.assertTrue(home)
        self.assertTrue(home.block_ids)

    def test_site_publish_workflow(self):
        brief = self.env['rn.ai.site.brief'].create({
            'name': 'Salon Launch',
            'business_name': 'Glow Salon',
            'business_type': 'salon',
            'description': 'Hair and beauty services.',
            'company_id': self.env.company.id,
        })
        brief.action_generate_site()
        site = brief.site_id
        site.action_publish()
        self.assertEqual(site.state, 'published')
        self.assertEqual(brief.state, 'published')

    def test_dashboard_data(self):
        self.env['rn.ai.site.brief'].create({
            'name': 'Clinic Brief',
            'business_name': 'City Clinic',
            'business_type': 'clinic',
            'description': 'Family healthcare.',
            'company_id': self.env.company.id,
        })
        data = self.env['rn.ai.site.dashboard.service'].get_dashboard_data()
        self.assertIn('cards', data)
        self.assertGreaterEqual(data['cards']['briefs'], 1)

    def test_settings_service(self):
        settings = self.env['rn.ai.site.brief.service'].ensure_default_settings()
        self.assertEqual(settings.company_id, self.env.company)
