# -*- coding: utf-8 -*-
"""Temple departments."""

from odoo import fields, models


class RnTempleDepartment(models.Model):
    """Operational department: ritual, kitchen, admin, security, etc."""

    _name = 'rn.temple.department'
    _description = 'Temple Department'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    branch_id = fields.Many2one('rn.temple.branch', string='Branch')
    department_type = fields.Selection(
        selection=[
            ('ritual', 'Ritual / Worship'),
            ('kitchen', 'Kitchen / Annadhanam'),
            ('admin', 'Administration'),
            ('accounts', 'Accounts'),
            ('security', 'Security'),
            ('maintenance', 'Maintenance'),
            ('events', 'Events'),
            ('volunteer', 'Volunteers'),
            ('other', 'Other'),
        ],
        default='ritual',
        required=True,
    )
    manager_id = fields.Many2one('rn.temple.priest', string='Department Head')
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
