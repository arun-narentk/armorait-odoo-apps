# -*- coding: utf-8 -*-
"""Timeline templates map model states to visual timeline nodes."""

from __future__ import annotations

from odoo import fields, models

from odoo.addons.rn_record_timeline.services.constants import (
    EVENT_TYPE_SELECTION,
    FILTER_CATEGORY_SELECTION,
)


class RnTimelineTemplate(models.Model):
    """Configurable mapping from document states to timeline labels."""

    _name = 'rn.timeline.template'
    _description = 'Timeline Template'
    _order = 'model_id, sequence, id'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        'ir.model',
        required=True,
        ondelete='cascade',
        index=True,
    )
    model_name = fields.Char(related='model_id.model', store=True, index=True)
    state_from = fields.Char(
        help='Optional source state. Leave empty to match any previous state.',
    )
    state_to = fields.Char(
        required=True,
        help='Target state that triggers this timeline node.',
    )
    event_type = fields.Selection(
        selection=EVENT_TYPE_SELECTION,
        required=True,
        default='other',
    )
    event_label = fields.Char(
        required=True,
        translate=True,
        help='Label shown on the timeline node.',
    )
    icon = fields.Char(default='fa-circle')
    color = fields.Char(default='#64748b')
    sequence = fields.Integer(default=10)
    filter_category = fields.Selection(
        selection=FILTER_CATEGORY_SELECTION,
        default='general',
        required=True,
    )
    company_id = fields.Many2one('res.company')

    _sql_constraints = [
        (
            'rn_timeline_template_unique_transition',
            'unique(model_id, state_from, state_to, company_id)',
            'Each state transition template must be unique per model and company.',
        ),
    ]
