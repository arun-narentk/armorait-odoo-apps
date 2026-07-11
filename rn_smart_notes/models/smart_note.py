# -*- coding: utf-8 -*-
"""Context-aware sticky notes attached to any business record."""

import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError

from odoo.addons.rn_smart_notes.constants import (
    COLOR_CSS,
    NOTE_COLORS,
    NOTE_ICONS,
    NOTE_PRIORITIES,
    NOTE_VISIBILITY,
)

_logger = logging.getLogger(__name__)


class RnSmartNote(models.Model):
    _name = 'rn.smart.note'
    _description = 'Smart Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'is_pinned desc, priority_order desc, sequence, id desc'

    name = fields.Char(required=True, tracking=True)
    note = fields.Html(sanitize=True)
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Many2oneReference(
        string='Related Document',
        model_field='res_model',
        required=True,
        index=True,
    )
    color = fields.Selection(NOTE_COLORS, default='yellow', required=True)
    priority = fields.Selection(NOTE_PRIORITIES, default='medium', required=True)
    priority_order = fields.Integer(compute='_compute_priority_order', store=True)
    icon = fields.Selection(NOTE_ICONS, default='general', required=True)
    is_pinned = fields.Boolean(default=False, tracking=True)
    visibility = fields.Selection(NOTE_VISIBILITY, default='everyone', required=True)
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    reminder_date = fields.Datetime(string='Reminder')
    reminder_activity_id = fields.Many2one('mail.activity', copy=False)
    mention_user_ids = fields.Many2many(
        'res.users',
        'rn_smart_note_mention_user_rel',
        'note_id',
        'user_id',
        string='Mentioned Users',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'rn_smart_note_attachment_rel',
        'note_id',
        'attachment_id',
        string='Attachments',
    )
    template_id = fields.Many2one('rn.smart.note.template', string='Template')
    record_display_name = fields.Char(compute='_compute_record_display_name')

    @api.depends('priority')
    def _compute_priority_order(self):
        weights = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        for record in self:
            record.priority_order = weights.get(record.priority, 0)

    @api.depends('res_model', 'res_id')
    def _compute_record_display_name(self):
        for record in self:
            display = ''
            if record.res_model and record.res_id:
                target = self.env[record.res_model].browse(record.res_id)
                if target.exists():
                    display = target.display_name
            record.record_display_name = display

    @api.model_create_multi
    def create(self, vals_list):
        service = self.env['rn.smart.note.service']
        notes = super().create(vals_list)
        for note in notes:
            service.after_note_create(note)
        return notes

    def write(self, vals):
        service = self.env['rn.smart.note.service']
        old_pins = {note.id: note.is_pinned for note in self}
        result = super().write(vals)
        if 'mention_user_ids' in vals:
            for note in self:
                service.notify_mentions(note)
        if 'reminder_date' in vals:
            for note in self:
                service.sync_reminder_activity(note)
        if 'is_pinned' in vals:
            for note in self:
                if old_pins.get(note.id) != note.is_pinned:
                    service.log_pin_change(note)
        return result

    def unlink(self):
        for note in self:
            if note.reminder_activity_id:
                note.reminder_activity_id.unlink()
        return super().unlink()

    def action_toggle_pin(self):
        self.ensure_one()
        self.is_pinned = not self.is_pinned
        return True

    def action_open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _check_private_access(self):
        self.ensure_one()
        user = self.env.user
        if self.visibility == 'only_me' and self.user_id != user:
            if not user.has_group('rn_smart_notes.group_rn_smart_notes_manager'):
                raise AccessError(_('This note is private.'))

    @api.model
    def get_panel_data(self, res_model, res_id):
        """Return notes and templates for the OWL side panel."""
        if not res_model or not res_id:
            return {'notes': [], 'templates': [], 'quick_templates': []}
        if res_model not in self.env:
            raise UserError(_('Unsupported model: %s') % res_model)
        target = self.env[res_model].browse(res_id)
        if not target.exists():
            return {'notes': [], 'templates': [], 'quick_templates': []}
        if not target.has_access('read'):
            raise AccessError(_('You cannot read this document.'))

        notes = self.search(
            self._panel_domain(res_model, res_id),
            order='is_pinned desc, priority_order desc, sequence, id desc',
        )
        templates = self.env['rn.smart.note.template'].search(
            [('active', '=', True)],
            order='sequence, name',
        )
        return {
            'notes': [note._note_to_panel_dict() for note in notes],
            'templates': [template._to_panel_dict() for template in templates],
            'quick_templates': templates.filtered('is_quick')._to_quick_list(),
        }

    @api.model
    def _panel_domain(self, res_model, res_id):
        return [
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
            ('active', '=', True),
        ]

    def _note_to_panel_dict(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'note': self.note or '',
            'color': self.color,
            'color_css': COLOR_CSS.get(self.color, '#fef3c7'),
            'priority': self.priority,
            'icon': self.icon,
            'is_pinned': self.is_pinned,
            'visibility': self.visibility,
            'user_name': self.user_id.name,
            'create_age': self._format_relative_age(self.create_date),
            'reminder_date': fields.Datetime.to_string(self.reminder_date) if self.reminder_date else False,
            'mention_user_ids': self.mention_user_ids.ids,
            'attachment_count': len(self.attachment_ids),
        }

    @api.model
    def _format_relative_age(self, dt_value):
        if not dt_value:
            return ''
        delta = fields.Datetime.now() - dt_value
        days = delta.days
        if days <= 0:
            return _('Today')
        if days == 1:
            return _('Yesterday')
        return _('%s days ago') % days

    @api.model
    def create_from_panel(self, res_model, res_id, values):
        service = self.env['rn.smart.note.service']
        return service.add_note(res_model, res_id, values)

    @api.model
    def update_from_panel(self, note_id, values):
        note = self.browse(note_id)
        note._check_private_access()
        allowed = {
            'name', 'note', 'color', 'priority', 'icon', 'is_pinned',
            'visibility', 'reminder_date', 'mention_user_ids',
        }
        write_vals = {key: val for key, val in values.items() if key in allowed}
        if write_vals:
            note.write(write_vals)
        return note._note_to_panel_dict()

    @api.model
    def delete_from_panel(self, note_id):
        note = self.browse(note_id)
        if note.user_id != self.env.user and not self.env.user.has_group(
            'rn_smart_notes.group_rn_smart_notes_manager'
        ):
            raise AccessError(_('You can only delete your own notes.'))
        note.unlink()
        return True
