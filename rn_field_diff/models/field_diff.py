# -*- coding: utf-8 -*-

from odoo import fields, models

from ..constants import CHANGE_CATEGORY_SELECTION, COLOR_CLASS_SELECTION, FIELD_TYPE_SELECTION, FILTER_CATEGORY_SELECTION


class RnFieldDiff(models.Model):
    _name = 'rn.field.diff'
    _description = 'Field Difference'
    _order = 'changed_on desc, id desc'

    name = fields.Char(required=True, index=True)
    model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    field_name = fields.Char(required=True, index=True)
    field_label = fields.Char(required=True)
    field_type = fields.Selection(selection=FIELD_TYPE_SELECTION, required=True, index=True)
    old_value_display = fields.Text()
    new_value_display = fields.Text()
    difference_display = fields.Char()
    difference_numeric = fields.Float()
    change_category = fields.Selection(
        selection=CHANGE_CATEGORY_SELECTION,
        default='modified',
        required=True,
        index=True,
    )
    color_class = fields.Selection(
        selection=COLOR_CLASS_SELECTION,
        default='blue',
        required=True,
    )
    filter_category = fields.Selection(
        selection=FILTER_CATEGORY_SELECTION,
        default='other',
        index=True,
    )
    mail_message_id = fields.Many2one('mail.message', required=True, ondelete='cascade', index=True)
    tracking_value_id = fields.Many2one('mail.tracking.value', ondelete='cascade', index=True)
    user_id = fields.Many2one('res.partner', string='Changed By', index=True)
    changed_on = fields.Datetime(index=True)
    company_id = fields.Many2one('res.company', index=True)

    def name_get(self):
        return [(rec.id, '%s: %s' % (rec.field_label, rec.change_category)) for rec in self]
