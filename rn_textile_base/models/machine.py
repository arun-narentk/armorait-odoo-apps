# -*- coding: utf-8 -*-
"""Machine registry."""

from odoo import api, fields, models


class RnTextileMachine(models.Model):
    """Production machine or utility asset."""

    _name = 'rn.textile.machine'
    _description = 'Textile Machine'
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
    department_id = fields.Many2one(
        'rn.textile.department',
        string='Department',
        index=True,
        domain="[('factory_id', '=', factory_id)]",
    )
    machine_type = fields.Selection(
        selection=[
            ('knitting', 'Knitting Machine'),
            ('dyeing', 'Dyeing Machine'),
            ('loom', 'Loom'),
            ('compressor', 'Compressor'),
            ('boiler', 'Boiler'),
            ('generator', 'Generator'),
            ('stenter', 'Stenter'),
            ('compactor', 'Compactor'),
            ('cutting', 'Cutting Table'),
            ('sewing', 'Sewing Machine'),
            ('other', 'Other'),
        ],
        default='knitting',
        required=True,
        tracking=True,
    )
    manufacturer = fields.Char()
    model_no = fields.Char(string='Model Number')
    serial_no = fields.Char(string='Serial Number')
    capacity_per_day = fields.Float(string='Daily Capacity', help='Units per day (kg, meters, pieces)')
    capacity_uom_id = fields.Many2one('uom.uom', string='Capacity UoM')
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('idle', 'Idle'),
            ('maintenance', 'Under Maintenance'),
            ('breakdown', 'Breakdown'),
            ('retired', 'Retired'),
        ],
        default='active',
        tracking=True,
    )
    operator_id = fields.Many2one('hr.employee', string='Assigned Operator')
    company_id = fields.Many2one(
        related='factory_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.textile.machine') or 'New'
        return super().create(vals_list)

    @api.onchange('factory_id')
    def _onchange_factory_id(self):
        if self.department_id and self.department_id.factory_id != self.factory_id:
            self.department_id = False

    @api.model
    def _cron_maintenance_reminder(self):
        """Notify supervisors about machines under maintenance or breakdown."""
        machines = self.search([
            ('state', 'in', ('maintenance', 'breakdown')),
            ('active', '=', True),
        ], limit=50)
        for machine in machines:
            machine.message_post(
                body='Machine requires attention. Review maintenance schedule and spare parts.',
                message_type='notification',
            )
