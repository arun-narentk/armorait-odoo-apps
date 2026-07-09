# -*- coding: utf-8 -*-
"""Downtime events logged from terminals or IoT."""

from odoo import api, fields, models


class RnMesDowntimeEvent(models.Model):
    """Machine or line downtime with duration and reason."""

    _name = 'rn.mes.downtime.event'
    _description = 'MES Downtime Event'
    _inherit = ['mail.thread']
    _order = 'start_time desc'

    name = fields.Char(compute='_compute_name', store=True)
    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    machine_id = fields.Many2one('rn.mes.machine.device', string='Machine Device')
    reason_id = fields.Many2one('rn.mes.downtime.reason', required=True, index=True)
    session_id = fields.Many2one('rn.mes.production.session')
    workorder_id = fields.Many2one('mrp.workorder')
    operator_id = fields.Many2one('hr.employee', string='Reported By')
    start_time = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    end_time = fields.Datetime()
    duration_minutes = fields.Float(compute='_compute_duration', store=True)
    note = fields.Text()
    state = fields.Selection(
        [
            ('open', 'Open'),
            ('closed', 'Closed'),
        ],
        default='open',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('workcenter_id.name', 'reason_id.name', 'start_time')
    def _compute_name(self):
        for rec in self:
            wc = rec.workcenter_id.name or ''
            reason = rec.reason_id.name or ''
            when = fields.Datetime.to_string(rec.start_time) if rec.start_time else ''
            rec.name = f'{wc} - {reason} ({when})' if wc else reason or 'Downtime'

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.duration_minutes = round(delta.total_seconds() / 60.0, 2)
            else:
                rec.duration_minutes = 0.0
