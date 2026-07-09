# -*- coding: utf-8 -*-
"""Detailed recognition history for auditing and accuracy metrics."""

from odoo import fields, models


class RnHrRecognitionHistory(models.Model):
    """Fine-grained history of each recognition pipeline stage."""

    _name = 'rn.hr.recognition.history'
    _description = 'Face Recognition History'
    _order = 'create_date desc'

    name = fields.Char(required=True, default='History')
    log_id = fields.Many2one(
        'rn.hr.attendance.log',
        string='Attendance Log',
        ondelete='cascade',
        index=True,
    )
    event_type = fields.Selection(
        selection=[
            ('detect', 'Face Detected'),
            ('embed', 'Embedding Generated'),
            ('match', 'Match'),
            ('reject', 'Reject'),
            ('spoof', 'Spoof'),
            ('attendance', 'Attendance Created'),
            ('error', 'Error'),
        ],
        required=True,
        index=True,
    )
    duration_ms = fields.Integer(string='Duration (ms)')
    payload = fields.Text(help='JSON debug payload for admins.')
    company_id = fields.Many2one(
        'res.company',
        related='log_id.company_id',
        store=True,
    )
