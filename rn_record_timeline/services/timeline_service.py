# -*- coding: utf-8 -*-
"""Timeline engine service layer."""

from __future__ import annotations

import logging
from typing import Any

from odoo import _, api, fields, models

from odoo.addons.rn_record_timeline.services.constants import (
    DEFAULT_EVENT_META,
    TIMELINE_PAGE_LIMIT,
)

_logger = logging.getLogger(__name__)


class RnTimelineService(models.AbstractModel):
    """Create, query, and render timeline events for supported documents."""

    _name = 'rn.timeline.service'
    _description = 'Record Timeline Service'

    @api.model
    def _event_meta(self, event_type: str) -> dict[str, str]:
        return DEFAULT_EVENT_META.get(event_type, DEFAULT_EVENT_META['other'])

    @api.model
    def create_event(
        self,
        record,
        name: str,
        event_type: str = 'other',
        *,
        filter_category: str = 'general',
        related_model: str | None = None,
        related_res_id: int | None = None,
        description: str | None = None,
        icon: str | None = None,
        color: str | None = None,
        sequence: int = 10,
        event_date: fields.Datetime | None = None,
    ):
        """Persist one timeline node for a business record."""
        meta = self._event_meta(event_type)
        company_id = getattr(record, 'company_id', False)
        values = {
            'name': name,
            'model': record._name,
            'record_id': record.id,
            'event_type': event_type,
            'filter_category': filter_category,
            'icon': icon or meta['icon'],
            'color': color or meta['color'],
            'sequence': sequence,
            'related_model': related_model,
            'related_res_id': related_res_id,
            'description': description,
            'date': event_date or fields.Datetime.now(),
            'company_id': company_id.id if company_id else self.env.company.id,
        }
        return self.env['rn.timeline.event'].sudo().create(values)

    @api.model
    def find_template(self, record, state_from: str | None, state_to: str):
        """Return the best matching template for a state transition."""
        Template = self.env['rn.timeline.template']
        company = getattr(record, 'company_id', False) or self.env.company
        domain = [
            ('model_name', '=', record._name),
            ('state_to', '=', state_to),
            ('active', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company.id),
        ]
        templates = Template.search(domain, order='sequence, id')
        for template in templates:
            if not template.state_from or template.state_from == (state_from or ''):
                return template
        return Template.browse()

    @api.model
    def log_state_transition(self, record, old_state: str | None, new_state: str):
        """Create a timeline node when a tracked state changes."""
        if old_state == new_state:
            return self.env['rn.timeline.event']
        template = self.find_template(record, old_state, new_state)
        if template:
            return self.create_event(
                record,
                template.event_label,
                event_type=template.event_type,
                filter_category=template.filter_category,
                icon=template.icon,
                color=template.color,
                sequence=template.sequence,
            )
        label = new_state.replace('_', ' ').title() if new_state else _('Updated')
        return self.create_event(
            record,
            label,
            event_type='other',
            filter_category='general',
        )

    @api.model
    def get_events(
        self,
        record,
        *,
        filter_category: str | None = None,
        limit: int = TIMELINE_PAGE_LIMIT,
        offset: int = 0,
    ):
        return self.env['rn.timeline.event'].search_for_record(
            record._name,
            record.id,
            filter_category=filter_category,
            limit=limit,
            offset=offset,
        )

    @api.model
    def render_timeline(
        self,
        record,
        *,
        filter_category: str | None = None,
        limit: int = TIMELINE_PAGE_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Return JSON payload for the OWL timeline widget."""
        events = self.get_events(
            record,
            filter_category=filter_category,
            limit=limit,
            offset=offset,
        )
        total = self.env['rn.timeline.event'].count_for_record(
            record._name,
            record.id,
            filter_category=filter_category,
        )
        return {
            'record': {
                'model': record._name,
                'id': record.id,
                'name': record.display_name,
            },
            'events': [
                {
                    'id': event.id,
                    'name': event.name,
                    'date': fields.Datetime.to_string(event.date),
                    'user': event.user_id.name,
                    'event_type': event.event_type,
                    'icon': event.icon,
                    'color': event.color,
                    'filter_category': event.filter_category,
                    'description': event.description or '',
                    'related_model': event.related_model,
                    'related_res_id': event.related_res_id,
                }
                for event in events
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + len(events)) < total,
        }

    @api.model
    def export_timeline_pdf_action(self, record):
        """Return report action for timeline PDF export."""
        report_map = {
            'sale.order': 'rn_record_timeline.action_report_timeline_pdf',
            'purchase.order': 'rn_record_timeline.action_report_timeline_purchase',
            'account.move': 'rn_record_timeline.action_report_timeline_invoice',
            'crm.lead': 'rn_record_timeline.action_report_timeline_crm',
        }
        xmlid = report_map.get(record._name, 'rn_record_timeline.action_report_timeline_pdf')
        return self.env.ref(xmlid).report_action(record)
