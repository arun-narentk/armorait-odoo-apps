# -*- coding: utf-8 -*-
"""Dashboard-level filter definition."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .constants import DATE_FILTER_TYPE_SELECTION, FILTER_TYPE_SELECTION


class RnKpiDashboardFilter(models.Model):
    """Filter applied across compatible dashboard items."""

    _name = 'rn.kpi.dashboard.filter'
    _description = 'KPI Dashboard Filter'
    _order = 'sequence, id'

    dashboard_id = fields.Many2one(
        'rn.kpi.dashboard',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10, index=True)
    active = fields.Boolean(default=True)
    filter_type = fields.Selection(
        selection=FILTER_TYPE_SELECTION,
        required=True,
        default='date',
        index=True,
    )
    field_name = fields.Char(index=True)
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete='set null')
    operator = fields.Char(default='=')
    value = fields.Char()
    value_from = fields.Char()
    value_to = fields.Char()
    date_filter_type = fields.Selection(
        selection=DATE_FILTER_TYPE_SELECTION,
    )
    model_mapping = fields.Json(
        help='Optional map of model technical name to field name for cross-model filter propagation.',
    )
    company_id = fields.Many2one(
        related='dashboard_id.company_id',
        store=True,
        index=True,
        readonly=True,
    )

    _filter_dashboard_seq_idx = models.Index('(dashboard_id, sequence, id)')

    @api.onchange('field_id')
    def _onchange_field_id(self):
        for flt in self:
            if flt.field_id:
                flt.field_name = flt.field_id.name

    @api.constrains('filter_type', 'date_filter_type', 'value_from', 'value_to', 'field_name')
    def _check_filter_config(self):
        for flt in self:
            if flt.filter_type == 'date' and not flt.date_filter_type:
                raise ValidationError(_(
                    'Date filter "%s" requires a date filter type.',
                    flt.name,
                ))
            if flt.date_filter_type == 'custom':
                if flt.value_from and flt.value_to and flt.value_from > flt.value_to:
                    raise ValidationError(_(
                        'Filter "%s" custom range is invalid (from > to).',
                        flt.name,
                    ))
            if flt.filter_type in ('selection', 'many2one', 'many2many', 'numeric', 'text') and not flt.field_name:
                raise ValidationError(_(
                    'Filter "%s" requires a field name.',
                    flt.name,
                ))

    def get_configuration(self):
        self.ensure_one()
        return {
            'name': self.name,
            'sequence': self.sequence,
            'active': self.active,
            'filter_type': self.filter_type,
            'field_name': self.field_name or (self.field_id.name if self.field_id else False),
            'operator': self.operator or '=',
            'value': self.value or False,
            'value_from': self.value_from or False,
            'value_to': self.value_to or False,
            'date_filter_type': self.date_filter_type or False,
            'model_mapping': self.model_mapping or {},
        }
