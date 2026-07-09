# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolParentGuardian(models.Model):
    _name = 'rn.school.parent.guardian'
    _description = 'Parent / Guardian'

    student_id = fields.Many2one('rn.school.student', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    relation = fields.Selection(
        [
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
            ('other', 'Other'),
        ],
        default='father',
    )
    mobile = fields.Char()
    email = fields.Char()
    partner_id = fields.Many2one('res.partner', string='Portal Contact')
    is_primary = fields.Boolean(string='Primary Contact')
