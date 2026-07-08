# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnHrAttendanceFaceSkeleton(TransactionCase):
    """Phase 1 tests for module skeleton and core models."""

    def test_security_groups_exist(self):
        """Verify security groups are installed."""
        group = self.env.ref('rn_hr_attendance_face.group_rn_face_officer', raise_if_not_found=False)
        self.assertTrue(group)

    def test_employee_face_create(self):
        """Create a draft face profile for an employee."""
        employee = self.env['hr.employee'].create({'name': 'Face Test Employee'})
        face = self.env['rn.hr.employee.face'].create({
            'employee_id': employee.id,
            'status': 'draft',
        })
        self.assertEqual(face.name, employee.name)
        self.assertEqual(face.status, 'draft')

    def test_embedding_roundtrip(self):
        """Embedding helper encodes and decodes vectors."""
        service = self.env['rn.hr.embedding.service']
        token = service.encrypt_embedding([0.1, 0.2, 0.3])
        vector = service.decrypt_embedding(token)
        self.assertEqual(vector, [0.1, 0.2, 0.3])

    def test_recognition_settings_company_unique(self):
        """Company can own recognition settings."""
        settings = self.env['rn.hr.recognition.settings'].create({
            'name': 'Default Settings',
            'company_id': self.env.company.id,
        })
        self.assertTrue(settings.matching_threshold > 0)
