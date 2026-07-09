# -*- coding: utf-8 -*-
"""Shop-floor work order execution service."""

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnMesExecutionService(models.AbstractModel):
    """Start, pause, resume, and complete jobs from tablet or backend."""

    _name = 'rn.mes.execution.service'
    _description = 'MES Execution Service'

    def _log_event(self, session, event_type, quantity=0.0, note=''):
        return self.env['rn.mes.production.event'].create({
            'session_id': session.id,
            'event_type': event_type,
            'quantity': quantity,
            'note': note,
        })

    def start_job(self, terminal_id, operator_id, workorder_id):
        terminal = self.env['rn.mes.terminal'].browse(terminal_id)
        operator = self.env['hr.employee'].browse(operator_id)
        workorder = self.env['mrp.workorder'].browse(workorder_id)
        if not terminal.exists():
            raise UserError(_('Terminal not found.'))
        if not operator.exists():
            raise UserError(_('Operator not found.'))
        if not workorder.exists():
            raise UserError(_('Work order not found.'))
        if terminal.session_id and terminal.session_id.state == 'active':
            raise UserError(_('Terminal already has an active session.'))

        session = self.env['rn.mes.production.session'].create({
            'terminal_id': terminal.id,
            'operator_id': operator.id,
            'workorder_id': workorder.id,
            'state': 'active',
        })
        terminal.session_id = session.id
        workorder.write({
            'mes_state': 'running',
            'mes_session_id': session.id,
        })
        if workorder.state not in ('progress', 'done'):
            workorder.button_start()
        self._log_event(session, 'start')
        return session.id

    def pause_job(self, session_id, note=''):
        session = self.env['rn.mes.production.session'].browse(session_id)
        if not session.exists() or session.state != 'active':
            raise UserError(_('No active session to pause.'))
        session.state = 'paused'
        session.workorder_id.mes_state = 'paused'
        self._log_event(session, 'pause', note=note)
        return True

    def resume_job(self, session_id):
        session = self.env['rn.mes.production.session'].browse(session_id)
        if not session.exists() or session.state != 'paused':
            raise UserError(_('Session is not paused.'))
        session.state = 'active'
        session.workorder_id.mes_state = 'running'
        self._log_event(session, 'resume')
        return True

    def record_scrap(self, session_id, quantity, scrap_type='scrap', reason='', note=''):
        session = self.env['rn.mes.production.session'].browse(session_id)
        if not session.exists():
            raise UserError(_('Session not found.'))
        qty = float(quantity or 0.0)
        if qty <= 0:
            raise UserError(_('Quantity must be positive.'))
        self.env['rn.mes.scrap.record'].create({
            'session_id': session.id,
            'product_id': session.workorder_id.product_id.id,
            'scrap_type': scrap_type,
            'quantity': qty,
            'reason': reason,
            'note': note,
        })
        if scrap_type == 'reject':
            session.reject_qty += qty
            session.workorder_id.mes_reject_qty += qty
        else:
            session.scrap_qty += qty
            session.workorder_id.mes_scrap_qty += qty
        self._log_event(session, 'scrap', quantity=qty, note=reason or note)
        return True

    def complete_job(self, session_id, good_qty=0.0, note=''):
        session = self.env['rn.mes.production.session'].browse(session_id)
        if not session.exists():
            raise UserError(_('Session not found.'))
        settings = session.company_id._get_mes_settings()
        if settings.require_quality_on_complete:
            pending = self.env['rn.mes.quality.inspection'].search_count([
                ('workorder_id', '=', session.workorder_id.id),
                ('state', 'in', ('draft', 'in_progress', 'fail')),
            ])
            if pending:
                raise UserError(_('Complete quality inspection before finishing the job.'))

        good = float(good_qty or 0.0)
        session.good_qty += good
        session.state = 'done'
        session.end_time = fields.Datetime.now()
        wo = session.workorder_id
        wo.mes_good_qty += good
        wo.mes_state = 'done'
        wo.mes_session_id = False
        session.terminal_id.session_id = False
        self._log_event(session, 'complete', quantity=good, note=note)
        return True

    def get_tablet_payload(self, terminal_id=None, workorder_id=None):
        """Data bundle for OWL shop-floor tablet."""
        terminal = self.env['rn.mes.terminal'].browse(terminal_id) if terminal_id else False
        workorder = self.env['mrp.workorder'].browse(workorder_id) if workorder_id else False
        session = terminal.session_id if terminal else workorder.mes_session_id

        pending_wos = self.env['mrp.workorder'].search([
            ('state', 'in', ('ready', 'progress')),
            ('mes_state', 'in', ('pending', 'paused')),
            ('company_id', '=', self.env.company.id),
        ], limit=20, order='date_start asc')

        return {
            'terminal': {
                'id': terminal.id,
                'name': terminal.name,
                'code': terminal.code,
            } if terminal else {},
            'session': {
                'id': session.id,
                'state': session.state,
                'operator': session.operator_id.name,
                'good_qty': session.good_qty,
                'scrap_qty': session.scrap_qty,
                'reject_qty': session.reject_qty,
            } if session else {},
            'workorder': {
                'id': workorder.id,
                'name': workorder.name,
                'product': workorder.product_id.display_name,
                'qty': workorder.qty_production,
                'mes_state': workorder.mes_state,
                'instruction_url': workorder.mes_instruction_url or '',
            } if workorder else {},
            'pending_workorders': [
                {
                    'id': wo.id,
                    'name': wo.name,
                    'product': wo.product_id.display_name,
                    'workcenter': wo.workcenter_id.name,
                }
                for wo in pending_wos
            ],
        }
