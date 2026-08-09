# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'rn_hr_resume_ai_parser')
class TestRnHrResumeAiParser(TransactionCase):

    def test_service_model_exists(self):
        self.assertIn('resume.ai.parser.service', self.env)
        self.assertIn('hr.resume.similarity', self.env)

    def test_ranking_action_exists(self):
        action = self.env.ref(
            'rn_hr_resume_ai_parser.hr_applicant_action_ai_ranking',
            raise_if_not_found=False,
        )
        self.assertTrue(action)

    def test_applicant_fields_present(self):
        fields_map = self.env['hr.applicant']._fields
        self.assertIn('parsing_status', fields_map)
