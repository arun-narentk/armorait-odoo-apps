# -*- coding: utf-8 -*-
"""KPI dashboard item / visualization configuration."""

import ast
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .constants import (
    AGGREGATION_SELECTION,
    CHART_ITEM_TYPES,
    COLOR_PALETTE_SELECTION,
    DATA_SOURCE_TYPE_SELECTION,
    DATE_GRANULARITY_SELECTION,
    ITEM_TYPE_SELECTION,
    NUMBER_FORMAT_SELECTION,
    SORT_ORDER_SELECTION,
)

_logger = logging.getLogger(__name__)


class RnKpiDashboardItem(models.Model):
    """Single visualization card on a KPI dashboard."""

    _name = 'rn.kpi.dashboard.item'
    _description = 'KPI Dashboard Item'
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
    item_type = fields.Selection(
        selection=ITEM_TYPE_SELECTION,
        required=True,
        default='tile',
        index=True,
    )
    chart_type = fields.Selection(
        selection=ITEM_TYPE_SELECTION,
        help='Active visualization type. Kept in sync with item_type; used when switching charts without rebuilding measures.',
    )
    model_id = fields.Many2one('ir.model', string='Model', ondelete='set null', index=True)
    model_name = fields.Char(
        related='model_id.model',
        store=True,
        index=True,
        readonly=True,
    )
    domain = fields.Char(default='[]')
    context = fields.Char(default='{}')
    group_by = fields.Char(help='Comma-separated field names for grouping.')
    measure_field_ids = fields.Many2many(
        'ir.model.fields',
        'rn_kpi_dashboard_item_measure_rel',
        'item_id',
        'field_id',
        string='Measure Fields',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['integer', 'float', 'monetary'])]",
    )
    measure = fields.Char(help='Primary measure field technical name (shortcut).')
    date_field = fields.Char(help='Date/datetime field technical name used for time grouping and filters.')
    date_granularity = fields.Selection(
        selection=DATE_GRANULARITY_SELECTION,
        default='month',
    )
    sort_field = fields.Char()
    sort_order = fields.Selection(
        selection=SORT_ORDER_SELECTION,
        default='desc',
    )
    limit = fields.Integer(default=80)
    aggregation = fields.Selection(
        selection=AGGREGATION_SELECTION,
        default='count',
        required=True,
    )
    x_axis_field = fields.Char()
    y_axis_field = fields.Char()
    secondary_axis_field = fields.Char()
    dimensions = fields.Json(
        help='Normalized dimension definitions for multi-axis visualizations.',
    )
    measures = fields.Json(
        help='Normalized measure definitions including formulas.',
    )
    color_palette = fields.Selection(
        selection=COLOR_PALETTE_SELECTION,
        default='default',
        required=True,
    )
    custom_colors = fields.Json(
        help='Optional map of segment label to color.',
    )
    number_format = fields.Selection(
        selection=NUMBER_FORMAT_SELECTION,
        default='number',
        required=True,
    )
    decimal_places = fields.Integer(default=2)
    currency_field = fields.Char()
    show_legend = fields.Boolean(default=True)
    show_labels = fields.Boolean(default=True)
    show_values = fields.Boolean(default=False)
    show_title = fields.Boolean(default=True)
    title = fields.Char()
    subtitle = fields.Char()
    icon = fields.Char()
    icon_color = fields.Char(default='#0f4c81')
    tile_size = fields.Selection(
        selection=[
            ('sm', 'Small'),
            ('md', 'Medium'),
            ('lg', 'Large'),
        ],
        default='md',
    )
    layout_x = fields.Integer(default=0)
    layout_y = fields.Integer(default=0)
    layout_width = fields.Integer(default=4)
    layout_height = fields.Integer(default=3)
    min_width = fields.Integer(default=2)
    min_height = fields.Integer(default=2)
    drilldown_enabled = fields.Boolean(default=False)
    drilldown_action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Drill-down Action',
        ondelete='set null',
    )
    target_action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Target Action',
        ondelete='set null',
    )
    filter_config = fields.Json()
    formula_config = fields.Json(
        help='Sandboxed formula measure configuration (evaluated in Phase 13).',
    )
    data_source_type = fields.Selection(
        selection=DATA_SOURCE_TYPE_SELECTION,
        default='odoo',
        required=True,
    )
    external_file_id = fields.Many2one(
        'ir.attachment',
        string='External File',
        ondelete='set null',
        help='CSV/XLSX source attachment. Dedicated external source model arrives later.',
    )
    refresh_interval = fields.Integer(
        string='Item Refresh Interval (seconds)',
        default=0,
        help='0 inherits dashboard refresh settings.',
    )
    animation_enabled = fields.Boolean(default=True)
    animation_config = fields.Json()
    css_class = fields.Char()
    style_config = fields.Json()
    company_id = fields.Many2one(
        related='dashboard_id.company_id',
        store=True,
        index=True,
        readonly=True,
    )
    item_filter_ids = fields.One2many(
        'rn.kpi.dashboard.item.filter',
        'item_id',
        string='Item Filters',
        copy=True,
    )

    _layout_width_positive = models.Constraint(
        'CHECK(layout_width > 0)',
        'Layout width must be positive.',
    )
    _layout_height_positive = models.Constraint(
        'CHECK(layout_height > 0)',
        'Layout height must be positive.',
    )
    _limit_non_negative = models.Constraint(
        'CHECK(limit >= 0)',
        'Limit cannot be negative.',
    )
    _decimal_places_non_negative = models.Constraint(
        'CHECK(decimal_places >= 0)',
        'Decimal places cannot be negative.',
    )
    _item_dashboard_seq_idx = models.Index('(dashboard_id, sequence, id)')
    _item_model_type_idx = models.Index('(model_name, item_type)')

    @api.onchange('item_type')
    def _onchange_item_type(self):
        for item in self:
            item.chart_type = item.item_type

    @api.onchange('chart_type')
    def _onchange_chart_type(self):
        for item in self:
            if item.chart_type:
                item.item_type = item.chart_type

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for item in self:
            item.measure_field_ids = [(5, 0, 0)]
            item.measure = False
            item.date_field = False
            item.group_by = False
            item.x_axis_field = False
            item.y_axis_field = False
            item.secondary_axis_field = False
            item.sort_field = False
            item.currency_field = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('chart_type') and vals.get('item_type'):
                vals['chart_type'] = vals['item_type']
            if not vals.get('title') and vals.get('name'):
                vals['title'] = vals['name']
        records = super().create(vals_list)
        records.validate_configuration()
        return records

    def write(self, vals):
        if vals.get('item_type') and 'chart_type' not in vals:
            vals = dict(vals, chart_type=vals['item_type'])
        if vals.get('chart_type') and 'item_type' not in vals:
            vals = dict(vals, item_type=vals['chart_type'])
        res = super().write(vals)
        config_keys = {
            'item_type', 'chart_type', 'model_id', 'domain', 'context', 'group_by',
            'measure', 'measure_field_ids', 'aggregation', 'limit', 'data_source_type',
            'layout_width', 'layout_height', 'min_width', 'min_height', 'x_axis_field',
            'y_axis_field', 'date_field', 'formula_config',
        }
        if config_keys.intersection(vals):
            self.validate_configuration()
        return res

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.setdefault('name', _('%s (copy)', self.name))
        return super().copy(default)

    def duplicate_item(self, target_dashboard=None):
        """Duplicate this item, optionally onto another dashboard."""
        self.ensure_one()
        default = {}
        if target_dashboard:
            if target_dashboard._name != 'rn.kpi.dashboard':
                raise UserError(_('Target must be a KPI dashboard.'))
            default['dashboard_id'] = target_dashboard.id
        return self.copy(default)

    def action_duplicate_item(self):
        self.ensure_one()
        new_item = self.duplicate_item()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicated Item'),
            'res_model': self._name,
            'res_id': new_item.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.constrains(
        'layout_width', 'layout_height', 'min_width', 'min_height',
        'domain', 'context', 'aggregation', 'measure', 'item_type',
        'data_source_type', 'model_id', 'decimal_places', 'refresh_interval',
    )
    def _check_configuration(self):
        self.validate_configuration()

    def validate_configuration(self):
        """Validate item configuration. Raises ValidationError on hard failures."""
        for item in self:
            item._validate_layout()
            item._validate_domain_context()
            item._validate_data_source()
            item._validate_measures()
            if item.refresh_interval < 0:
                raise ValidationError(_('Item refresh interval cannot be negative.'))
            if item.decimal_places < 0:
                raise ValidationError(_('Decimal places cannot be negative.'))
        return True

    def _validate_layout(self):
        self.ensure_one()
        if self.layout_width < self.min_width:
            raise ValidationError(_(
                'Layout width (%s) cannot be smaller than min width (%s).',
                self.layout_width,
                self.min_width,
            ))
        if self.layout_height < self.min_height:
            raise ValidationError(_(
                'Layout height (%s) cannot be smaller than min height (%s).',
                self.layout_height,
                self.min_height,
            ))

    def _validate_domain_context(self):
        self.ensure_one()
        for field_name, expected in (('domain', list), ('context', dict)):
            raw = self[field_name] or ('[]' if expected is list else '{}')
            try:
                value = ast.literal_eval(raw)
            except (SyntaxError, ValueError) as exc:
                raise ValidationError(_(
                    'Invalid %(field)s on item "%(name)s": %(error)s',
                    field=field_name,
                    name=self.name,
                    error=exc,
                )) from exc
            if not isinstance(value, expected):
                raise ValidationError(_(
                    'Item "%(name)s" %(field)s must be a %(type)s.',
                    name=self.name,
                    field=field_name,
                    type=expected.__name__,
                ))

    def _validate_data_source(self):
        self.ensure_one()
        if self.data_source_type == 'odoo':
            if self.item_type != 'todo' and not self.model_id:
                raise ValidationError(_(
                    'Item "%s" requires an Odoo model.',
                    self.name,
                ))
            if self.model_id and self.model_id.model not in self.env:
                raise ValidationError(_(
                    'Model "%s" is not available in this database.',
                    self.model_id.model,
                ))
        elif self.data_source_type in ('csv', 'xlsx') and not self.external_file_id:
            # Soft requirement until external source phase: warn via logs only.
            _logger.info(
                'Dashboard item %s uses %s without an attached file yet.',
                self.id,
                self.data_source_type,
            )

    def _validate_measures(self):
        self.ensure_one()
        if self.aggregation != 'count' and self.data_source_type == 'odoo' and self.model_id:
            if not self.measure and not self.measure_field_ids and not self.measures:
                if self.item_type in CHART_ITEM_TYPES or self.item_type == 'tile':
                    raise ValidationError(_(
                        'Item "%s" requires a measure field for %s aggregation.',
                        self.name,
                        self.aggregation,
                    ))
        if self.model_name and self.model_name in self.env:
            Model = self.env[self.model_name]
            for field_name in filter(None, [
                self.measure,
                self.date_field,
                self.x_axis_field,
                self.y_axis_field,
                self.secondary_axis_field,
                self.sort_field,
                self.currency_field,
            ]):
                if field_name not in Model._fields:
                    raise ValidationError(_(
                        'Field "%(field)s" does not exist on model "%(model)s" (item "%(name)s").',
                        field=field_name,
                        model=self.model_name,
                        name=self.name,
                    ))
            if self.group_by:
                for field_name in [part.strip() for part in self.group_by.split(',') if part.strip()]:
                    # Allow date:field:granularity style later; for now accept bare field names.
                    bare = field_name.split(':')[0]
                    if bare not in Model._fields:
                        raise ValidationError(_(
                            'Group-by field "%(field)s" does not exist on model "%(model)s".',
                            field=bare,
                            model=self.model_name,
                        ))
            for field in self.measure_field_ids:
                if field.model != self.model_name:
                    raise ValidationError(_(
                        'Measure field "%s" does not belong to model "%s".',
                        field.name,
                        self.model_name,
                    ))

    def get_configuration(self):
        """Return a portable item configuration for UI, export, and AI layers."""
        self.ensure_one()
        return {
            'name': self.name,
            'sequence': self.sequence,
            'active': self.active,
            'item_type': self.item_type,
            'chart_type': self.chart_type or self.item_type,
            'model': self.model_name or False,
            'domain': self.domain or '[]',
            'context': self.context or '{}',
            'group_by': self.group_by or '',
            'measure': self.measure or False,
            'measure_fields': self.measure_field_ids.mapped('name'),
            'date_field': self.date_field or False,
            'date_granularity': self.date_granularity or False,
            'sort_field': self.sort_field or False,
            'sort_order': self.sort_order or 'desc',
            'limit': self.limit,
            'aggregation': self.aggregation,
            'x_axis_field': self.x_axis_field or False,
            'y_axis_field': self.y_axis_field or False,
            'secondary_axis_field': self.secondary_axis_field or False,
            'dimensions': self.dimensions or [],
            'measures': self.measures or [],
            'color_palette': self.color_palette,
            'custom_colors': self.custom_colors or {},
            'number_format': self.number_format,
            'decimal_places': self.decimal_places,
            'currency_field': self.currency_field or False,
            'show_legend': self.show_legend,
            'show_labels': self.show_labels,
            'show_values': self.show_values,
            'show_title': self.show_title,
            'title': self.title or self.name,
            'subtitle': self.subtitle or '',
            'icon': self.icon or '',
            'icon_color': self.icon_color or '',
            'tile_size': self.tile_size,
            'layout': {
                'x': self.layout_x,
                'y': self.layout_y,
                'width': self.layout_width,
                'height': self.layout_height,
                'min_width': self.min_width,
                'min_height': self.min_height,
            },
            'drilldown_enabled': self.drilldown_enabled,
            'drilldown_action': (
                self.drilldown_action_id.get_external_id().get(self.drilldown_action_id.id)
                if self.drilldown_action_id else False
            ),
            'target_action': (
                self.target_action_id.get_external_id().get(self.target_action_id.id)
                if self.target_action_id else False
            ),
            'filter_config': self.filter_config or {},
            'formula_config': self.formula_config or {},
            'data_source_type': self.data_source_type,
            'refresh_interval': self.refresh_interval,
            'animation_enabled': self.animation_enabled,
            'animation_config': self.animation_config or {},
            'css_class': self.css_class or '',
            'style_config': self.style_config or {},
            'item_filters': [
                flt.get_configuration() for flt in self.item_filter_ids.sorted('sequence')
            ],
        }

    def get_data(self, dashboard_filters=None, options=None):
        """Fetch normalized visualization data via the secure data engine."""
        self.ensure_one()
        return self.env['rn.kpi.dashboard.data.service'].fetch_item_data(
            self,
            dashboard_filters=dashboard_filters,
            options=options,
        )
