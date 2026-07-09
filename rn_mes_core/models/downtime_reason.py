# -*- coding: utf-8 -*-
"""Downtime reason master data."""

from odoo import fields, models


class RnMesDowntimeReason(models.Model):
    """Standard downtime categories for OEE loss tracking."""

    _name = 'rn.mes.downtime.reason'
    _description = 'MES Downtime Reason'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    category = fields.Selection(
        [
            ('planned', 'Planned'),
            ('unplanned', 'Unplanned'),
        ],
        default='unplanned',
        required=True,
    )
    loss_type = fields.Selection(
        [
            ('availability', 'Availability Loss'),
            ('performance', 'Performance Loss'),
            ('quality', 'Quality Loss'),
        ],
        default='availability',
        required=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )
