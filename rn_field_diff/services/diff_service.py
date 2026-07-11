# -*- coding: utf-8 -*-
"""Field diff service: format tracked values and build structured comparisons."""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime

from odoo import _, api, fields, models

from ..constants import CHANGE_CATEGORY_SELECTION, COLOR_CLASS_SELECTION, FIELD_TYPE_SELECTION, FILTER_CATEGORY_SELECTION

_logger = logging.getLogger(__name__)


class RnFieldDiffService(models.AbstractModel):
    _name = 'rn.field.diff.service'
    _description = 'Field Difference Service'

    @api.model
    def _filter_category_for_type(self, field_type: str) -> str:
        if field_type in {'integer', 'float', 'monetary'}:
            return 'numeric'
        if field_type in {'date', 'datetime'}:
            return 'date'
        if field_type in {'char', 'text', 'selection'}:
            return 'text'
        if field_type in {'many2one', 'many2many', 'one2many', 'tags'}:
            return 'relational'
        if field_type == 'boolean':
            return 'boolean'
        return 'other'

    @api.model
    def _format_boolean(self, value) -> str:
        if value in (False, None, '', 0):
            return _('Disabled')
        return _('Enabled')

    @api.model
    def _display_from_tracking(self, tracking, field_type: str, *, new: bool) -> str:
        values = tracking._format_display_value(field_type, new=new)
        if not values:
            return ''
        value = values[0]
        if field_type == 'boolean':
            return self._format_boolean(value)
        if value in (False, None):
            return ''
        return str(value)

    @api.model
    def _calculate_numeric_diff(self, old_value, new_value, field_type: str) -> tuple[str, float | bool]:
        try:
            old_num = float(old_value or 0)
            new_num = float(new_value or 0)
        except (TypeError, ValueError):
            return '', 0.0
        delta = new_num - old_num
        if field_type == 'monetary':
            sign = '+' if delta >= 0 else ''
            return f'{sign}{delta:,.2f}', delta
        if field_type == 'integer':
            sign = '+' if delta >= 0 else ''
            return f'{sign}{int(delta)}', delta
        sign = '+' if delta >= 0 else ''
        pct = ''
        if old_num:
            pct_val = (delta / old_num) * 100
            pct = f' ({sign}{pct_val:.0f}%)'
        return f'{sign}{delta:g}{pct}', delta

    @api.model
    def _calculate_date_diff(self, old_value, new_value, field_type: str) -> tuple[str, float | bool]:
        if not old_value or not new_value:
            return '', 0.0
        try:
            if field_type == 'date':
                old_dt = fields.Date.from_string(str(old_value)[:10])
                new_dt = fields.Date.from_string(str(new_value)[:10])
            else:
                old_dt = fields.Datetime.from_string(str(old_value).replace('Z', ''))
                new_dt = fields.Datetime.from_string(str(new_value).replace('Z', ''))
            days = (new_dt - old_dt).days
            sign = '+' if days >= 0 else ''
            label = _('%(sign)s%(days)s Days', sign=sign, days=days)
            return label, float(days)
        except Exception as exc:
            _logger.debug('Date diff failed: %s', exc)
            return '', 0.0

    @api.model
    def _parse_relational_sets(self, old_display: str, new_display: str) -> tuple[str, str, str]:
        old_items = {item.strip() for item in (old_display or '').split(',') if item.strip()}
        new_items = {item.strip() for item in (new_display or '').split(',') if item.strip()}
        added = sorted(new_items - old_items)
        removed = sorted(old_items - new_items)
        parts = []
        if added:
            parts.append('%s: %s' % (_('Added'), ', '.join(added)))
        if removed:
            parts.append('%s: %s' % (_('Removed'), ', '.join(removed)))
        if added and not removed and not (old_items & new_items):
            category = 'added'
            color = 'green'
        elif removed and not added and not (old_items & new_items):
            category = 'removed'
            color = 'red'
        else:
            category = 'modified'
            color = 'blue'
        return category, color, ' | '.join(parts) if parts else ''

    @api.model
    def build_diff_payload(self, tracking) -> dict:
        """Build rn.field.diff values from a mail.tracking.value record."""
        message = tracking.mail_message_id
        model_name = tracking.field_id.model or message.model
        field_name = tracking.field_id.name or (tracking.field_info or {}).get('name', 'unknown')
        field_type = tracking.field_id.ttype or (tracking.field_info or {}).get('type', 'char')
        if field_type == 'properties':
            field_type = (tracking.field_info or {}).get('type', 'char')
        if field_type == 'tags':
            field_type = 'many2many'

        allowed_types = {item[0] for item in FIELD_TYPE_SELECTION}
        stored_field_type = field_type if field_type in allowed_types else 'other'

        col_info = {'type': field_type, 'string': tracking.field_id.field_description}
        if tracking.field_info:
            col_info['string'] = tracking.field_info.get('desc') or col_info['string']

        old_display = self._display_from_tracking(tracking, field_type, new=False)
        new_display = self._display_from_tracking(tracking, field_type, new=True)

        difference_display = ''
        difference_numeric = 0.0
        change_category = 'modified'
        color_class = 'blue'

        if field_type in {'integer', 'float', 'monetary'}:
            old_raw = tracking._format_display_value(field_type, new=False)
            new_raw = tracking._format_display_value(field_type, new=True)
            difference_display, difference_numeric = self._calculate_numeric_diff(
                old_raw[0] if old_raw else 0,
                new_raw[0] if new_raw else 0,
                field_type,
            )
        elif field_type in {'date', 'datetime'}:
            old_raw = tracking._format_display_value(field_type, new=False)
            new_raw = tracking._format_display_value(field_type, new=True)
            difference_display, difference_numeric = self._calculate_date_diff(
                old_raw[0] if old_raw else False,
                new_raw[0] if new_raw else False,
                field_type,
            )
        elif field_type in {'many2many', 'one2many', 'tags'}:
            change_category, color_class, difference_display = self._parse_relational_sets(
                old_display, new_display,
            )
        elif field_type == 'boolean':
            if not old_display and new_display:
                change_category, color_class = 'added', 'green'
            elif old_display and not new_display:
                change_category, color_class = 'removed', 'red'

        return {
            'name': col_info['string'] or field_name,
            'model': model_name,
            'res_id': message.res_id,
            'field_name': field_name,
            'field_label': col_info['string'] or field_name,
            'field_type': stored_field_type,
            'old_value_display': old_display,
            'new_value_display': new_display,
            'difference_display': difference_display,
            'difference_numeric': difference_numeric,
            'change_category': change_category,
            'color_class': color_class,
            'filter_category': self._filter_category_for_type(field_type),
            'mail_message_id': message.id,
            'tracking_value_id': tracking.id,
            'user_id': message.author_id.id or message.create_uid.id,
            'changed_on': message.date,
            'company_id': message.record_company_id.id if message.record_company_id else self.env.company.id,
        }

    @api.model
    def sync_from_tracking(self, tracking):
        payload = self.build_diff_payload(tracking)
        if not payload.get('model') or not payload.get('res_id'):
            return self.env['rn.field.diff']
        existing = self.env['rn.field.diff'].sudo().search([
            ('tracking_value_id', '=', tracking.id),
        ], limit=1)
        if existing:
            return existing
        return self.env['rn.field.diff'].sudo().create(payload)

    @api.model
    def get_record_diffs(self, model_name, res_id, **filters):
        domain = [('model', '=', model_name), ('res_id', '=', res_id)]
        if filters.get('filter_category'):
            domain.append(('filter_category', '=', filters['filter_category']))
        if filters.get('user_id'):
            domain.append(('user_id', '=', filters['user_id']))
        if filters.get('date_from'):
            domain.append(('changed_on', '>=', filters['date_from']))
        if filters.get('date_to'):
            domain.append(('changed_on', '<=', filters['date_to']))
        return self.env['rn.field.diff'].search(domain, order='changed_on desc, id desc')

    @api.model
    def get_summary(self, model_name, res_id) -> dict:
        diffs = self.get_record_diffs(model_name, res_id)
        by_filter = {}
        for diff in diffs:
            by_filter[diff.filter_category] = by_filter.get(diff.filter_category, 0) + 1
        return {
            'total': len(diffs),
            'numeric': by_filter.get('numeric', 0),
            'date': by_filter.get('date', 0),
            'text': by_filter.get('text', 0),
            'relational': by_filter.get('relational', 0),
            'boolean': by_filter.get('boolean', 0),
            'other': by_filter.get('other', 0),
        }

    @api.model
    def get_diffs_for_web(self, model_name, res_id, limit=50):
        diffs = self.get_record_diffs(model_name, res_id)[:limit]
        return [{
            'id': diff.id,
            'field_label': diff.field_label,
            'field_type': diff.field_type,
            'old_value': diff.old_value_display,
            'new_value': diff.new_value_display,
            'difference': diff.difference_display,
            'color_class': diff.color_class,
            'change_category': diff.change_category,
            'user': diff.user_id.display_name,
            'changed_on': fields.Datetime.to_string(diff.changed_on) if diff.changed_on else '',
        } for diff in diffs]

    @api.model
    def export_csv(self, diff_ids) -> bytes:
        diffs = self.env['rn.field.diff'].browse(diff_ids)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            'Model', 'Record ID', 'Field', 'Type', 'Before', 'After',
            'Difference', 'Changed By', 'Changed On',
        ])
        for diff in diffs:
            writer.writerow([
                diff.model,
                diff.res_id,
                diff.field_label,
                diff.field_type,
                diff.old_value_display,
                diff.new_value_display,
                diff.difference_display,
                diff.user_id.display_name,
                diff.changed_on,
            ])
        return buffer.getvalue().encode('utf-8')
