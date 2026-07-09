# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolInsightService(models.AbstractModel):
    _name = 'rn.school.insight.service'
    _description = 'School AI Insight Service'

    def get_risk_score(self, student_id):
        student = self.env['rn.school.student'].browse(student_id)
        if not student.exists() or student.state != 'enrolled':
            return 0
        score = 0
        att_rate = 100.0
        if student.class_id:
            att_rate = self.env['rn.school.attendance.service'].get_class_attendance_rate(
                student.class_id.id, days=30
            )
        if att_rate < 75:
            score += 40
        elif att_rate < 85:
            score += 20
        results = self.env['rn.school.exam.result'].search([
            ('student_id', '=', student.id),
        ], limit=3, order='id desc')
        if results:
            avg = sum(results.mapped('percentage')) / len(results)
            if avg < 50:
                score += 40
            elif avg < 65:
                score += 25
        pending_hw = self.env['rn.school.homework.submission'].search_count([
            ('student_id', '=', student.id),
            ('state', '=', 'pending'),
            ('homework_id.due_date', '<', fields.Datetime.now()),
        ])
        if pending_hw >= 3:
            score += 20
        return min(score, 100)

    def draft_report_comment(self, result_id):
        result = self.env['rn.school.exam.result'].browse(result_id)
        if not result.exists():
            return ''
        student = result.student_id.name
        pct = result.percentage or 0
        if pct >= 85:
            tone = f'{student} has shown excellent progress and consistent effort.'
        elif pct >= 70:
            tone = f'{student} is performing well with scope to strengthen weaker topics.'
        elif pct >= 50:
            tone = f'{student} needs focused support to improve academic outcomes.'
        else:
            tone = f'{student} requires immediate academic intervention and closer monitoring.'
        return (
            f'{tone} Attendance and homework completion should be reviewed with parents. '
            f'Teacher to edit before publishing.'
        )

    def answer_analytics_question(self, question, company_id=None):
        company_id = company_id or self.env.company.id
        q = (question or '').lower()
        dash = self.env['rn.school.dashboard.service'].get_principal_dashboard(company_id)
        if 'attendance' in q:
            classes = self.env['rn.school.class'].search([('company_id', '=', company_id)])
            lowest = None
            for cls in classes:
                rate = self.env['rn.school.attendance.service'].get_class_attendance_rate(cls.id)
                if lowest is None or rate < lowest[1]:
                    lowest = (cls.name, rate)
            if lowest:
                return f'Lowest attendance class: {lowest[0]} at {lowest[1]}%.'
        if 'fee' in q or 'revenue' in q:
            return f'Outstanding fees: {dash["fees_outstanding"]}.'
        if 'admission' in q or 'enquiry' in q:
            return f'New admission enquiries: {dash["new_enquiries"]}.'
        return (
            f'Enrolled students: {dash["enrolled_students"]}, '
            f'outstanding fees: {dash["fees_outstanding"]}.'
        )

    def admission_assistant_reply(self, question):
        q = (question or '').lower()
        if 'document' in q or 'required' in q:
            return 'Required documents: birth certificate, previous school TC, photos, address proof.'
        if 'fee' in q or 'cost' in q:
            return 'Fees vary by grade. Submit an enquiry and our team will share the fee structure.'
        if 'process' in q or 'admission' in q:
            return 'Process: Enquiry, Application, Document verification, Interview, Approval, Fee payment.'
        return 'How can we help with admissions? Ask about documents, fees, or the application process.'
