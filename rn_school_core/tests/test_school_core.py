# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnSchoolCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.year = cls.env.ref('rn_school_core.academic_year_current')
        cls.env.company._get_school_settings().current_academic_year_id = cls.year.id
        cls.school_class = cls.env['rn.school.class'].create({
            'name': 'Grade 3 A',
            'grade_level': 3,
            'section': 'A',
            'academic_year_id': cls.year.id,
        })
        cls.env['rn.school.fee.structure'].create({
            'name': 'Grade 3 Fees',
            'academic_year_id': cls.year.id,
            'grade_level': 3,
            'tuition_fee': 30000,
            'installment_count': 3,
        })

    def test_student_admission_number(self):
        student = self.env['rn.school.student'].create({
            'name': 'Test Student',
            'academic_year_id': self.year.id,
            'class_id': self.school_class.id,
            'state': 'enrolled',
        })
        self.assertTrue(student.admission_number.startswith('ADM'))

    def test_admission_workflow(self):
        enquiry = self.env['rn.school.admission.enquiry'].create({
            'applicant_name': 'New Kid',
            'mobile': '9000000001',
            'grade_applied': 3,
        })
        enquiry.action_convert_application()
        app = enquiry.application_id
        app.action_verify_documents()
        app.action_schedule_interview()
        app.action_approve()
        student_id = self.env['rn.school.admission.service'].enroll_student(
            app.id, class_id=self.school_class.id
        )
        self.assertTrue(student_id)

    def test_attendance_session(self):
        student = self.env['rn.school.student'].create({
            'name': 'Att Student',
            'academic_year_id': self.year.id,
            'class_id': self.school_class.id,
            'state': 'enrolled',
        })
        session_id = self.env['rn.school.attendance.service'].create_session(self.school_class.id)
        session = self.env['rn.school.attendance.session'].browse(session_id)
        self.assertEqual(len(session.line_ids), 1)

    def test_exam_grade_and_ai_comment(self):
        student = self.env['rn.school.student'].create({
            'name': 'Exam Student',
            'academic_year_id': self.year.id,
            'state': 'enrolled',
        })
        exam = self.env['rn.school.exam'].create({
            'name': 'Unit Test 1',
            'academic_year_id': self.year.id,
            'subject': 'Math',
            'exam_date': '2025-06-01',
        })
        result = self.env['rn.school.exam.result'].create({
            'exam_id': exam.id,
            'student_id': student.id,
            'marks_obtained': 85,
        })
        self.assertEqual(result.grade, 'A')
        result.action_generate_ai_comment()
        self.assertTrue(result.ai_comment_draft)

    def test_principal_dashboard(self):
        data = self.env['rn.school.dashboard.service'].get_principal_dashboard()
        self.assertIn('enrolled_students', data)

    def test_admission_assistant(self):
        reply = self.env['rn.school.insight.service'].admission_assistant_reply(
            'What documents are required?'
        )
        self.assertIn('birth certificate', reply.lower())
