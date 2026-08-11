# -*- coding: utf-8 -*-
"""Secure ORM-based aggregation for Dashboard KPI Studio items."""

import ast
import logging

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression

from ..models.constants import EMPTY_DATA_PAYLOAD

_logger = logging.getLogger(__name__)

_AGGREGATION_MAP = {
    'count': '__count',
    'sum': 'sum',
    'avg': 'avg',
    'min': 'min',
    'max': 'max',
}


class RnKpiDashboardDataService(models.AbstractModel):
    """Fetch visualization payloads while respecting the current user rights."""

    _name = 'rn.kpi.dashboard.data.service'
    _description = 'KPI Dashboard Data Engine'

    @api.model
    def fetch_item_data(self, item, dashboard_filters=None, options=None):
        """Return a normalized payload for one dashboard item.

        Uses the caller's ORM rights only. Never elevates with sudo for data reads.
        """
        item.ensure_one()
        item.validate_configuration()
        payload = dict(EMPTY_DATA_PAYLOAD)
        payload['metadata'] = {
            'item_id': item.id,
            'item_type': item.item_type,
            'model': item.model_name or False,
            'aggregation': item.aggregation,
        }
        if dashboard_filters:
            payload['metadata']['dashboard_filters'] = dashboard_filters
        if options:
            payload['metadata']['options'] = options

        if item.data_source_type != 'odoo':
            payload['warnings'] = [
                _('Only Odoo model data sources are supported in this version.'),
            ]
            return payload

        if not item.model_name or item.model_name not in self.env:
            payload['warnings'] = [_('Configured model is missing or inaccessible.')]
            return payload

        try:
            Model = self.env[item.model_name]
            domain = self._build_domain(item, dashboard_filters)
            value, labels, datasets, records = self._aggregate(Model, item, domain)
        except AccessError:
            _logger.info(
                'Access denied fetching KPI item %s on model %s for uid %s',
                item.id,
                item.model_name,
                self.env.uid,
            )
            payload['warnings'] = [_('You do not have access to this model.')]
            return payload
        except (UserError, ValidationError, ValueError, SyntaxError) as exc:
            payload['warnings'] = [str(exc)]
            return payload

        payload.update({
            'labels': labels,
            'datasets': datasets,
            'records': records,
            'total': value,
            'value': value,
            'warnings': [],
        })
        return payload

    def _build_domain(self, item, dashboard_filters):
        """Combine item domain with optional dashboard filter clauses."""
        raw = item.domain or '[]'
        domain = ast.literal_eval(raw)
        if not isinstance(domain, list):
            raise ValidationError(_('Item domain must be a list.'))
        extra = []
        if dashboard_filters:
            if isinstance(dashboard_filters, list):
                extra = dashboard_filters
            elif isinstance(dashboard_filters, dict):
                extra = dashboard_filters.get('domain') or []
        if extra and not isinstance(extra, list):
            raise ValidationError(_('Dashboard filters domain must be a list.'))
        return expression.AND([domain, extra]) if extra else domain

    def _aggregate(self, Model, item, domain):
        """Run count or read_group aggregation for the item."""
        aggregation = item.aggregation or 'count'
        measure = (item.measure or '').strip()
        group_fields = [
            name.strip()
            for name in (item.group_by or '').split(',')
            if name.strip()
        ]

        if aggregation == 'count' and not group_fields:
            value = Model.search_count(domain)
            return value, [item.name], [{'label': item.name, 'data': [value]}], []

        if aggregation != 'count' and not measure:
            raise ValidationError(_(
                'Measure field is required for %(agg)s aggregation on "%(name)s".',
                agg=aggregation,
                name=item.name,
            ))

        if group_fields:
            return self._grouped_aggregate(Model, item, domain, aggregation, measure, group_fields)

        if aggregation == 'count':
            value = Model.search_count(domain)
        else:
            groups = Model.read_group(domain, [measure], [], lazy=False)
            value = groups[0].get(measure) if groups else 0
            if value is None:
                value = 0
        return value, [item.name], [{'label': item.name, 'data': [value]}], []

    def _grouped_aggregate(self, Model, item, domain, aggregation, measure, group_fields):
        """Aggregate with one or more group_by fields."""
        agg_key = _AGGREGATION_MAP.get(aggregation)
        if not agg_key:
            raise ValidationError(_('Unsupported aggregation: %s', aggregation))

        if aggregation == 'count':
            fields_list = []
        else:
            fields_list = ['%s:%s' % (measure, agg_key)]

        limit = item.limit or None
        groups = Model.read_group(
            domain,
            fields_list,
            group_fields,
            limit=limit,
            orderby=False,
            lazy=False,
        )
        labels = []
        data = []
        records = []
        # Odoo exposes aggregated measure under the field name; count under __count
        count_key = '__count'
        for group in groups:
            label_parts = []
            for field_name in group_fields:
                raw = group.get(field_name)
                if isinstance(raw, (list, tuple)) and raw:
                    label_parts.append(str(raw[1]))
                elif raw is False or raw is None:
                    label_parts.append(_('Undefined'))
                else:
                    label_parts.append(str(raw))
            label = ' / '.join(label_parts) if label_parts else _('Total')
            if aggregation == 'count':
                value = group.get(count_key) or 0
            else:
                value = group.get(measure)
                if value is None:
                    value = 0
            labels.append(label)
            data.append(value)
            records.append({
                'label': label,
                'value': value,
                'group': {fname: group.get(fname) for fname in group_fields},
            })
        total = sum(data) if aggregation in ('count', 'sum') else (data[0] if data else 0)
        datasets = [{'label': item.name, 'data': data}]
        return total, labels, datasets, records
