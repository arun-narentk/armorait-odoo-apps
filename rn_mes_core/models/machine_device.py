# -*- coding: utf-8 -*-
"""Machine and IoT gateway device registry."""

from odoo import fields, models


class RnMesMachineDevice(models.Model):
    """PLC, CNC, or sensor gateway connected to a work center."""

    _name = 'rn.mes.machine.device'
    _description = 'MES Machine Device'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True)
    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    protocol = fields.Selection(
        [
            ('manual', 'Manual'),
            ('mqtt', 'MQTT'),
            ('opc_ua', 'OPC UA'),
            ('modbus', 'Modbus'),
            ('plc', 'PLC'),
            ('cnc', 'CNC'),
        ],
        default='manual',
        required=True,
    )
    status = fields.Selection(
        [
            ('offline', 'Offline'),
            ('idle', 'Idle'),
            ('running', 'Running'),
            ('alarm', 'Alarm'),
            ('maintenance', 'Maintenance'),
        ],
        default='offline',
        tracking=True,
    )
    last_signal = fields.Datetime(string='Last Signal')
    gateway_url = fields.Char(string='Gateway URL')
    topic = fields.Char(help='MQTT topic or OPC node path')
    active = fields.Boolean(default=True)
    reading_ids = fields.One2many('rn.mes.machine.reading', 'device_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Device code must be unique per company.'),
    ]
