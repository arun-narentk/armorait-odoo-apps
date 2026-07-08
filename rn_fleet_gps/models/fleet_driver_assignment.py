# -*- coding: utf-8 -*-
"""Driver shift assignment history."""

from odoo import api, fields, models


class RnFleetDriverAssignment(models.Model):
    """Links drivers to vehicles for a shift window."""

    _name = 'rn.fleet.driver.assignment'
    _description = 'Fleet Driver Assignment'
    _order = 'date_start desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, index=True)
    driver_id = fields.Many2one('res.partner', string='Driver', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_start = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    date_end = fields.Datetime()
    state = fields.Selection(
        selection=[
            ('open', 'On Shift'),
            ('closed', 'Closed'),
        ],
        default='open',
        index=True,
    )
    rating = fields.Float(string='Driver Rating')
    violations = fields.Integer()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.depends('vehicle_id', 'driver_id')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s / %s' % (rec.vehicle_id.name or '', rec.driver_id.name or '')

    def action_close(self):
        self.write({
            'state': 'closed',
            'date_end': fields.Datetime.now(),
        })
        return True
