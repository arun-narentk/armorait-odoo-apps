# -*- coding: utf-8 -*-
"""Share wizard popup."""

from odoo import api, fields, models, _


class RnRecordShareWizard(models.TransientModel):
    _name = 'rn.record.share.wizard'
    _description = 'Record Share Wizard'

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    label = fields.Char(readonly=True)
    internal_url = fields.Char(readonly=True)
    hash_url = fields.Char(readonly=True)
    preview_url = fields.Text(readonly=True)
    preview_markdown = fields.Text(readonly=True)
    preview_html = fields.Text(readonly=True)
    preview_json = fields.Text(readonly=True)
    qr_installed = fields.Boolean(readonly=True)

    @api.model
    def open_for_record(self, res_model, res_id):
        payload = self.env['rn.record.share.service'].get_share_payload(res_model, res_id)
        wizard = self.create({
            'res_model': res_model,
            'res_id': res_id,
            'label': payload['label'],
            'internal_url': payload['internal_url'],
            'hash_url': payload['hash_url'],
            'preview_url': payload['formats']['url'],
            'preview_markdown': payload['formats']['markdown'],
            'preview_html': payload['formats']['html'],
            'preview_json': payload['formats']['json'],
            'qr_installed': payload['qr_installed'],
        })
        self.env['rn.record.share.service'].log_share(
            self.env[res_model].browse(res_id),
            'share',
            'url',
            payload['internal_url'],
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Share Record'),
            'res_model': 'rn.record.share.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_copy_url(self):
        return self.env['rn.record.share.service'].action_copy_format(
            self.res_model, self.res_id, 'url'
        )

    def action_copy_markdown(self):
        return self.env['rn.record.share.service'].action_copy_format(
            self.res_model, self.res_id, 'markdown'
        )

    def action_copy_html(self):
        return self.env['rn.record.share.service'].action_copy_format(
            self.res_model, self.res_id, 'html'
        )

    def action_copy_json(self):
        return self.env['rn.record.share.service'].action_copy_format(
            self.res_model, self.res_id, 'json'
        )

    def action_email(self):
        return self.env['rn.record.share.service'].action_email_share(
            self.res_model, self.res_id
        )

    def action_whatsapp(self):
        return self.env['rn.record.share.service'].action_whatsapp_share(
            self.res_model, self.res_id
        )

    def action_open_link(self):
        return self.env['rn.record.share.service'].action_open_internal(
            self.res_model, self.res_id
        )

    def action_generate_qr(self):
        record = self.env[self.res_model].browse(self.res_id)
        return self.env['rn.record.share.service'].open_qr_action(record)
