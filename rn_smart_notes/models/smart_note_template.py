# -*- coding: utf-8 -*-
"""Predefined note templates and quick-add presets."""

from odoo import fields, models

from odoo.addons.rn_smart_notes.constants import (
    NOTE_COLORS,
    NOTE_ICONS,
    NOTE_PRIORITIES,
    NOTE_VISIBILITY,
)


class RnSmartNoteTemplate(models.Model):
    _name = 'rn.smart.note.template'
    _description = 'Smart Note Template'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    description = fields.Html(sanitize=True)
    color = fields.Selection(NOTE_COLORS, default='yellow', required=True)
    priority = fields.Selection(NOTE_PRIORITIES, default='medium', required=True)
    icon = fields.Selection(NOTE_ICONS, default='general', required=True)
    visibility = fields.Selection(NOTE_VISIBILITY, default='everyone', required=True)
    is_quick = fields.Boolean(
        string='Quick Template',
        help='Show as a one-click quick note button in the document panel.',
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _to_panel_dict(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'color': self.color,
            'priority': self.priority,
            'icon': self.icon,
            'visibility': self.visibility,
            'is_quick': self.is_quick,
        }

    def _to_quick_list(self):
        return [template._to_panel_dict() for template in self]

    def apply_to_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            'note': self.description,
            'color': self.color,
            'priority': self.priority,
            'icon': self.icon,
            'visibility': self.visibility,
            'template_id': self.id,
        }
