# -*- coding: utf-8 -*-
"""IoT reading ingestion hooks."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMesIotService(models.AbstractModel):
    """Ingest machine telemetry from gateway (MQTT, OPC UA, Modbus)."""

    _name = 'rn.mes.iot.service'
    _description = 'MES IoT Service'

    def ingest_reading(self, device_code, metric, value_float=None, value_text=None):
        device = self.env['rn.mes.machine.device'].search([
            ('code', '=', device_code),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if not device:
            _logger.warning('MES IoT: unknown device %s', device_code)
            return False

        reading = self.env['rn.mes.machine.reading'].create({
            'device_id': device.id,
            'metric': metric,
            'value_float': value_float or 0.0,
            'value_text': value_text or '',
        })
        device.last_signal = fields.Datetime.now()
        if metric == 'status' and value_text:
            status_map = {
                'running': 'running',
                'idle': 'idle',
                'alarm': 'alarm',
                'offline': 'offline',
            }
            device.status = status_map.get(value_text, device.status)
        return reading.id

    def get_live_status(self, company_id=None):
        company_id = company_id or self.env.company.id
        devices = self.env['rn.mes.machine.device'].search([
            ('company_id', '=', company_id),
            ('active', '=', True),
        ])
        return [
            {
                'id': d.id,
                'name': d.name,
                'code': d.code,
                'workcenter': d.workcenter_id.name,
                'status': d.status,
                'protocol': d.protocol,
                'last_signal': fields.Datetime.to_string(d.last_signal) if d.last_signal else '',
            }
            for d in devices
        ]
