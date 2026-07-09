# -*- coding: utf-8 -*-
"""Employee / company HR documents."""

from odoo import fields, models


class RnHrmsDocument(models.Model):
    """Document attached to an employee or company policy library."""

    _name = 'rn.hrms.document'
    _description = 'HRMS Document'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    document_type = fields.Selection(
        selection=[
            ('id', 'Identity'),
            ('contract', 'Contract'),
            ('certificate', 'Certificate'),
            ('policy', 'Policy'),
            ('other', 'Other'),
        ],
        default='other',
        required=True,
    )
    employee_id = fields.Many2one('hr.employee', index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    attachment = fields.Binary(attachment=True)
    attachment_filename = fields.Char()
    expiry_date = fields.Date()
    is_private = fields.Boolean(default=True)
    note = fields.Text()
