# -*- coding: utf-8 -*-
"""Production lifecycle events from the shop floor."""

from odoo import fields, models


class RnMesProductionEvent(models.Model):
    """Start, pause, resume, complete, and note events."""

    _name = 'rn.mes.production.event'
    _description = 'MES Production Event'
    _order = 'event_time desc'

    session_id = fields.Many2one('rn.mes.production.session', required=True, ondelete='cascade', index=True)
    workorder_id = fields.Many2one(related='session_id.workorder_id', store=True, readonly=True)
    operator_id = fields.Many2one(related='session_id.operator_id', store=True, readonly=True)
    event_type = fields.Selection(
        [
            ('login', 'Operator Login'),
            ('start', 'Start Job'),
            ('pause', 'Pause'),
            ('resume', 'Resume'),
            ('complete', 'Complete'),
            ('scrap', 'Scrap Entry'),
            ('note', 'Note'),
            ('photo', 'Photo'),
        ],
        required=True,
        index=True,
    )
    event_time = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    quantity = fields.Float(digits='Product Unit')
    note = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Photos')
    company_id = fields.Many2one(
        related='session_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
