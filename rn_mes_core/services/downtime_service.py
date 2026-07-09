# -*- coding: utf-8 -*-
"""Downtime logging helpers."""

from odoo import fields, models
from odoo.exceptions import UserError


class RnMesDowntimeService(models.AbstractModel):
    """Open and close downtime events from tablet or IoT."""

    _name = 'rn.mes.downtime.service'
    _description = 'MES Downtime Service'

    def start_downtime(self, workcenter_id, reason_id, session_id=None, note=''):
        workcenter = self.env['mrp.workcenter'].browse(workcenter_id)
        reason = self.env['rn.mes.downtime.reason'].browse(reason_id)
        if not workcenter.exists() or not reason.exists():
            raise UserError('Work center and downtime reason are required.')
        open_evt = self.env['rn.mes.downtime.event'].search([
            ('workcenter_id', '=', workcenter.id),
            ('state', '=', 'open'),
        ], limit=1)
        if open_evt:
            raise UserError('Downtime is already open for this work center.')
        session = self.env['rn.mes.production.session'].browse(session_id) if session_id else False
        return self.env['rn.mes.downtime.event'].create({
            'workcenter_id': workcenter.id,
            'reason_id': reason.id,
            'session_id': session.id if session else False,
            'workorder_id': session.workorder_id.id if session else False,
            'operator_id': session.operator_id.id if session else False,
            'note': note,
            'state': 'open',
        }).id

    def end_downtime(self, event_id):
        event = self.env['rn.mes.downtime.event'].browse(event_id)
        if not event.exists() or event.state != 'open':
            raise UserError('Open downtime event not found.')
        event.write({
            'end_time': fields.Datetime.now(),
            'state': 'closed',
        })
        return True
