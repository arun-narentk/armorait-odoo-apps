# -*- coding: utf-8 -*-
"""Production departments and work centers."""

from odoo import fields, models


class RnTextileDepartment(models.Model):
    """Production department within a textile factory."""

    _name = 'rn.textile.department'
    _description = 'Textile Department'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    factory_id = fields.Many2one(
        'rn.textile.factory',
        required=True,
        ondelete='cascade',
        index=True,
    )
    department_type = fields.Selection(
        selection=[
            ('spinning', 'Spinning'),
            ('knitting', 'Knitting'),
            ('dyeing', 'Dyeing'),
            ('weaving', 'Weaving'),
            ('cutting', 'Cutting'),
            ('stitching', 'Stitching'),
            ('finishing', 'Finishing'),
            ('packing', 'Packing'),
            ('quality', 'Quality Control'),
            ('warehouse', 'Warehouse'),
            ('maintenance', 'Maintenance'),
            ('admin', 'Administration'),
            ('other', 'Other'),
        ],
        default='knitting',
        required=True,
    )
    manager_id = fields.Many2one('hr.employee', string='Department Head')
    machine_ids = fields.One2many('rn.textile.machine', 'department_id', string='Machines')
    machine_count = fields.Integer(compute='_compute_machine_count')
    company_id = fields.Many2one(
        related='factory_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    def _compute_machine_count(self):
        for dept in self:
            dept.machine_count = len(dept.machine_ids)

    def action_open_machines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Machines',
            'res_model': 'rn.textile.machine',
            'view_mode': 'list,form',
            'domain': [('department_id', '=', self.id)],
            'context': {'default_department_id': self.id, 'default_factory_id': self.factory_id.id},
        }
