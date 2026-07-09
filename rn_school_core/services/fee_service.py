# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import UserError


class RnSchoolFeeService(models.AbstractModel):
    _name = 'rn.school.fee.service'
    _description = 'Fee Service'

    def generate_installments(self, student_id, class_id=None):
        student = self.env['rn.school.student'].browse(student_id)
        if not student.exists():
            raise UserError('Student not found.')
        grade = student.class_id.grade_level if student.class_id else 0
        if class_id:
            grade = self.env['rn.school.class'].browse(class_id).grade_level
        structure = self.env['rn.school.fee.structure'].search([
            ('grade_level', '=', grade),
            ('academic_year_id', '=', student.academic_year_id.id),
            ('company_id', '=', student.company_id.id),
        ], limit=1)
        if not structure:
            return []
        count = max(structure.installment_count, 1)
        amount_each = structure.total_fee / count
        today = fields.Date.context_today(self)
        created = self.env['rn.school.fee.installment']
        for i in range(count):
            created |= self.env['rn.school.fee.installment'].create({
                'student_id': student.id,
                'fee_structure_id': structure.id,
                'name': f'Installment {i + 1}',
                'due_date': today + relativedelta(months=i),
                'amount': amount_each,
                'state': 'due',
            })
        return created.ids

    def create_invoice(self, installment_id):
        inst = self.env['rn.school.fee.installment'].browse(installment_id)
        if not inst.exists() or inst.state == 'paid':
            raise UserError('Invalid installment.')
        student = inst.student_id
        partner = student.partner_id
        if not partner:
            parent = student.parent_ids.filtered('is_primary')[:1]
            partner = self.env['res.partner'].create({
                'name': parent.name if parent else student.name,
                'phone': parent.mobile if parent else False,
                'email': parent.email if parent else False,
            })
            student.partner_id = partner.id
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': inst.name,
                'quantity': 1,
                'price_unit': inst.net_amount,
            })],
        })
        inst.write({'invoice_id': invoice.id})
        return invoice.id
