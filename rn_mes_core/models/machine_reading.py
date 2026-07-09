# -*- coding: utf-8 -*-
"""Sensor and machine telemetry readings."""

from odoo import fields, models


class RnMesMachineReading(models.Model):
    """Time-series value from a connected machine or sensor."""

    _name = 'rn.mes.machine.reading'
    _description = 'MES Machine Reading'
    _order = 'reading_time desc'

    device_id = fields.Many2one('rn.mes.machine.device', required=True, ondelete='cascade', index=True)
    workcenter_id = fields.Many2one(related='device_id.workcenter_id', store=True, readonly=True)
    metric = fields.Selection(
        [
            ('status', 'Status'),
            ('speed', 'Speed'),
            ('temperature', 'Temperature'),
            ('pressure', 'Pressure'),
            ('vibration', 'Vibration'),
            ('energy', 'Energy'),
            ('count', 'Production Count'),
            ('humidity', 'Humidity'),
            ('alarm', 'Alarm'),
        ],
        required=True,
        index=True,
    )
    value_float = fields.Float(string='Numeric Value')
    value_text = fields.Char(string='Text Value')
    reading_time = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    company_id = fields.Many2one(
        related='device_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
