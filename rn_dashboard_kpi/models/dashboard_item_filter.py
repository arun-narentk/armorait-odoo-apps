# -*- coding: utf-8 -*-
"""Item-specific filter overrides."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RnKpiDashboardItemFilter(models.Model):
    """Filter scoped to a single dashboard item."""

    _name = 'rn.kpi.dashboard.item.filter'
    _description = 'KPI Dashboard Item Filter'
    _order = 'sequence, id'

    item_id = fields.Many2one(
        'rn.kpi.dashboard.item',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    field_name = fields.Char(required=True)
    operator = fields.Char(default='=', required=True)
    value = fields.Char()
    value_from = fields.Char()
    value_to = fields.Char()

    _item_filter_seq_idx = models.Index('(item_id, sequence, id)')

    @api.constrains('field_name', 'item_id')
    def _check_field_on_model(self):
        for flt in self:
            model_name = flt.item_id.model_name
            if not model_name or model_name not in self.env:
                continue
            if flt.field_name not in self.env[model_name]._fields:
                raise ValidationError(_(
                    'Item filter field "%(field)s" does not exist on model "%(model)s".',
                    field=flt.field_name,
                    model=model_name,
                ))

    def get_configuration(self):
        self.ensure_one()
        return {
            'name': self.name,
            'sequence': self.sequence,
            'active': self.active,
            'field_name': self.field_name,
            'operator': self.operator or '=',
            'value': self.value or False,
            'value_from': self.value_from or False,
            'value_to': self.value_to or False,
        }
