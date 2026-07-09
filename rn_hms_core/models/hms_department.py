# -*- coding: utf-8 -*-
"""Hospital / clinic departments."""

from odoo import fields, models


class RnHmsDepartment(models.Model):
    """Clinical or support department."""

    _name = 'rn.hms.department'
    _description = 'HMS Department'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    department_type = fields.Selection(
        selection=[
            ('opd', 'OPD'),
            ('ipd', 'IPD'),
            ('lab', 'Laboratory'),
            ('radiology', 'Radiology'),
            ('pharmacy', 'Pharmacy'),
            ('admin', 'Administration'),
            ('other', 'Other'),
        ],
        default='opd',
        required=True,
    )
    manager_id = fields.Many2one('rn.hms.doctor', string='Head of Department')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
