# -*- coding: utf-8 -*-
"""Business logic for smart notes."""

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class RnSmartNoteService(models.AbstractModel):
    _name = 'rn.smart.note.service'
    _description = 'Smart Note Service'

    @api.model
    def add_note(self, res_model, res_id, values):
        if res_model not in self.env:
            raise ValueError(_('Unsupported model: %s') % res_model)
        target = self.env[res_model].browse(res_id)
        if not target.exists():
            raise ValueError(_('Record not found.'))
        if not target.has_access('write'):
            raise AccessError(_('You cannot add notes to this document.'))

        vals = dict(values or {})
        if vals.get('template_id'):
            template = self.env['rn.smart.note.template'].browse(vals['template_id'])
            if template.exists():
                template_vals = template.apply_to_values()
                template_vals.update({k: v for k, v in vals.items() if v})
                vals = template_vals

        company_id = vals.get('company_id')
        if not company_id and 'company_id' in target._fields:
            company_id = target.company_id.id
        if not company_id:
            company_id = self.env.company.id

        note_vals = {
            'name': vals.get('name') or _('New Note'),
            'note': vals.get('note'),
            'res_model': res_model,
            'res_id': res_id,
            'color': vals.get('color', 'yellow'),
            'priority': vals.get('priority', 'medium'),
            'icon': vals.get('icon', 'general'),
            'is_pinned': bool(vals.get('is_pinned')),
            'visibility': vals.get('visibility', 'everyone'),
            'reminder_date': vals.get('reminder_date'),
            'mention_user_ids': vals.get('mention_user_ids'),
            'template_id': vals.get('template_id'),
            'company_id': company_id,
            'user_id': self.env.user.id,
        }
        note = self.env['rn.smart.note'].create(note_vals)
        return note._note_to_panel_dict()

    @api.model
    def after_note_create(self, note):
        self.notify_mentions(note)
        self.sync_reminder_activity(note)
        self._post_document_message(note, _('Smart note added: %s') % note.name)
        target = self.env[note.res_model].browse(note.res_id)
        if target.exists() and 'smart_note_count' in target._fields:
            target.invalidate_recordset(['smart_note_count', 'smart_note_pinned_count'])

    @api.model
    def notify_mentions(self, note):
        if not note.mention_user_ids:
            return
        target = self.env[note.res_model].browse(note.res_id)
        if not target.exists():
            return
        partners = note.mention_user_ids.partner_id
        if not partners:
            return
        body = _('%(user)s mentioned you on note "%(note)s".') % {
            'user': self.env.user.name,
            'note': note.name,
        }
        target.message_notify(
            partner_ids=partners.ids,
            body=body,
            subject=note.name,
        )

    @api.model
    def sync_reminder_activity(self, note):
        if note.reminder_activity_id:
            note.reminder_activity_id.unlink()
            note.reminder_activity_id = False
        if not note.reminder_date:
            return
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return
        model = self.env['ir.model']._get(note.res_model)
        if not model:
            return
        deadline = fields.Datetime.to_datetime(note.reminder_date).date()
        activity = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'summary': note.name,
            'note': note.note,
            'date_deadline': deadline,
            'user_id': note.user_id.id,
            'res_model_id': model.id,
            'res_id': note.res_id,
        })
        note.reminder_activity_id = activity.id

    @api.model
    def log_pin_change(self, note):
        state = _('pinned') if note.is_pinned else _('unpinned')
        self._post_document_message(note, _('Smart note %s: %s') % (state, note.name))

    @api.model
    def _post_document_message(self, note, body):
        target = self.env[note.res_model].browse(note.res_id)
        if target.exists() and hasattr(target, 'message_post'):
            target.message_post(body=body, message_type='notification')

    @api.model
    def search_note_content(self, search_term, limit=50):
        domain = [
            ('active', '=', True),
            '|',
            ('name', 'ilike', search_term),
            ('note', 'ilike', search_term),
        ]
        return self.env['rn.smart.note'].search(domain, limit=limit)
