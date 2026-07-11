# -*- coding: utf-8 -*-
"""Timeline event records."""

from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import AccessError

from odoo.addons.rn_record_timeline.services.constants import (
    EVENT_TYPE_SELECTION,
    FILTER_CATEGORY_SELECTION,
)


class RnTimelineEvent(models.Model):
    """Audit-style timeline entry linked to any supported business document."""

    _name = 'rn.timeline.event'
    _description = 'Record Timeline Event'
    _order = 'date desc, sequence desc, id desc'
    _rec_name = 'name'

    name = fields.Char(required=True, translate=True)
    model = fields.Char(required=True, index=True)
    record_id = fields.Integer(required=True, index=True)
    date = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        index=True,
    )
    event_type = fields.Selection(
        selection=EVENT_TYPE_SELECTION,
        required=True,
        default='other',
        index=True,
    )
    icon = fields.Char(default='fa-circle')
    color = fields.Char(default='#64748b')
    sequence = fields.Integer(default=10)
    filter_category = fields.Selection(
        selection=FILTER_CATEGORY_SELECTION,
        default='general',
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        index=True,
    )
    related_model = fields.Char(index=True)
    related_res_id = fields.Integer(index=True)
    description = fields.Text()

    _sql_constraints = [
        (
            'rn_timeline_event_model_record_check',
            'CHECK(record_id > 0)',
            'Timeline events must reference a valid record.',
        ),
    ]

    def action_open_related_document(self):
        """Open the linked document from a timeline node."""
        self.ensure_one()
        if not self.related_model or not self.related_res_id:
            raise AccessError('This timeline event has no linked document.')
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': self.related_model,
            'view_mode': 'form',
            'res_id': self.related_res_id,
            'target': 'current',
        }

    @api.model
    def search_for_record(
        self,
        model: str,
        record_id: int,
        *,
        filter_category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        domain = [
            ('model', '=', model),
            ('record_id', '=', record_id),
        ]
        if filter_category and filter_category != 'all':
            domain.append(('filter_category', '=', filter_category))
        return self.search(domain, limit=limit, offset=offset, order='date desc, sequence desc, id desc')

    @api.model
    def count_for_record(
        self,
        model: str,
        record_id: int,
        *,
        filter_category: str | None = None,
    ) -> int:
        domain = [
            ('model', '=', model),
            ('record_id', '=', record_id),
        ]
        if filter_category and filter_category != 'all':
            domain.append(('filter_category', '=', filter_category))
        return self.search_count(domain)
