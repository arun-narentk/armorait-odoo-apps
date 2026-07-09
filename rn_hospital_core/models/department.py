# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalDepartment(models.Model):
    _name = 'rn.hospital.department'
    _description = 'Hospital Department'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    department_type = fields.Selection(
        [
            ('opd', 'OPD'),
            ('ipd', 'IPD'),
            ('lab', 'Laboratory'),
            ('radiology', 'Radiology'),
            ('pharmacy', 'Pharmacy'),
            ('ot', 'Operation Theatre'),
            ('admin', 'Administration'),
        ],
        default='opd',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )
