# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RnPreviewMixin(models.AbstractModel):
    _name = 'rn.preview.mixin'
    _description = 'Attachment Preview Mixin'

    rn_attachment_count = fields.Integer(
        string='Attachments',
        compute='_compute_rn_attachment_count',
    )
    rn_attachment_ids = fields.Many2many(
        'ir.attachment',
        compute='_compute_rn_attachment_ids',
        string='Record Attachments',
    )

    def _compute_rn_attachment_count(self):
        if not self.ids:
            for record in self:
                record.rn_attachment_count = 0
            return
        Attachment = self.env['ir.attachment']
        grouped = Attachment.read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'],
            ['res_id'],
        )
        counts = {row['res_id']: row['res_id_count'] for row in grouped}
        for record in self:
            record.rn_attachment_count = counts.get(record.id, 0)

    @api.depends('rn_attachment_count')
    def _compute_rn_attachment_ids(self):
        Attachment = self.env['ir.attachment']
        for record in self:
            if record.id:
                record.rn_attachment_ids = Attachment.search([
                    ('res_model', '=', record._name),
                    ('res_id', '=', record.id),
                ])
            else:
                record.rn_attachment_ids = Attachment.browse()

    def get_rn_attachment_preview_data(self):
        self.ensure_one()
        return self.env['rn.attachment.preview.service'].get_record_attachments(
            self._name,
            self.id,
        )

    def action_open_attachment_gallery(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id},
        }
