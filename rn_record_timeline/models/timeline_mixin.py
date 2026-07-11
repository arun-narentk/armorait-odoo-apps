# -*- coding: utf-8 -*-
"""Abstract mixin that adds timeline tracking to business documents."""

from __future__ import annotations

from odoo import _, api, fields, models

from odoo.addons.rn_record_timeline.services.constants import TIMELINE_PAGE_LIMIT


class RnTimelineMixin(models.AbstractModel):
    """Mixin for models that expose a visual record timeline."""

    _name = 'rn.timeline.mixin'
    _description = 'Record Timeline Mixin'

    timeline_event_count = fields.Integer(
        string='Timeline Events',
        compute='_compute_timeline_event_count',
    )

    @api.depends('write_date')
    def _compute_timeline_event_count(self):
        Event = self.env['rn.timeline.event']
        if not self.ids:
            for record in self:
                record.timeline_event_count = 0
            return
        grouped = Event.read_group(
            domain=[
                ('model', '=', self._name),
                ('record_id', 'in', self.ids),
            ],
            fields=['record_id'],
            groupby=['record_id'],
        )
        counts = {item['record_id'][0]: item['record_id_count'] for item in grouped}
        for record in self:
            record.timeline_event_count = counts.get(record.id, 0)

    def _timeline_state_field(self) -> str:
        """Return the state field tracked for timeline transitions."""
        if 'state' in self._fields:
            return 'state'
        return ''

    def _timeline_created_label(self) -> str:
        return _('Created')

    def _timeline_created_event_type(self) -> str:
        return 'created'

    def _timeline_created_filter_category(self) -> str:
        return 'general'

    def _get_timeline_events(
        self,
        filter_category: str | None = None,
        limit: int = TIMELINE_PAGE_LIMIT,
        offset: int = 0,
    ):
        self.ensure_one()
        return self.env['rn.timeline.service'].get_events(
            self,
            filter_category=filter_category,
            limit=limit,
            offset=offset,
        )

    def _add_timeline_event(
        self,
        name: str,
        event_type: str = 'other',
        **kwargs,
    ):
        self.ensure_one()
        return self.env['rn.timeline.service'].create_event(
            self,
            name,
            event_type=event_type,
            **kwargs,
        )

    def _render_timeline(
        self,
        filter_category: str | None = None,
        limit: int = TIMELINE_PAGE_LIMIT,
        offset: int = 0,
    ):
        self.ensure_one()
        return self.env['rn.timeline.service'].render_timeline(
            self,
            filter_category=filter_category,
            limit=limit,
            offset=offset,
        )

    def timeline_widget_data(
        self,
        filter_category: str | None = None,
        limit: int = TIMELINE_PAGE_LIMIT,
        offset: int = 0,
    ):
        """RPC entry point for the backend timeline widget."""
        self.ensure_one()
        return self._render_timeline(
            filter_category=filter_category,
            limit=limit,
            offset=offset,
        )

    def action_view_timeline(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timeline'),
            'res_model': 'rn.timeline.event',
            'view_mode': 'list,form',
            'domain': [
                ('model', '=', self._name),
                ('record_id', '=', self.id),
            ],
            'context': {
                'default_model': self._name,
                'default_record_id': self.id,
                'search_default_group_filter_category': 1,
            },
        }

    def action_export_timeline_pdf(self):
        self.ensure_one()
        return self.env['rn.timeline.service'].export_timeline_pdf_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.id:
                continue
            record._add_timeline_event(
                record._timeline_created_label(),
                event_type=record._timeline_created_event_type(),
                filter_category=record._timeline_created_filter_category(),
            )
        return records

    def write(self, vals):
        state_field = self._timeline_state_field()
        old_states = {}
        if state_field and state_field in vals:
            old_states = {record.id: getattr(record, state_field) for record in self}
        result = super().write(vals)
        if state_field and state_field in vals:
            service = self.env['rn.timeline.service']
            for record in self:
                previous = old_states.get(record.id)
                current = getattr(record, state_field)
                if previous != current:
                    service.log_state_transition(record, previous, current)
        return result
