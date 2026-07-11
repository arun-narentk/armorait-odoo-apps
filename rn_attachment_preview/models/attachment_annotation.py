# -*- coding: utf-8 -*-

from odoo import fields, models


class RnAttachmentAnnotation(models.Model):
    _name = 'rn.attachment.annotation'
    _description = 'Attachment Annotation'
    _order = 'page_number, id'

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Author',
        required=True,
        default=lambda self: self.env.user,
    )
    page_number = fields.Integer(string='Page', default=1)
    pos_x = fields.Float(string='Position X', default=10.0)
    pos_y = fields.Float(string='Position Y', default=10.0)
    note = fields.Text(string='Note', required=True)
    color = fields.Char(string='Color', default='#facc15')

    def to_panel_dict(self):
        self.ensure_one()
        return {
            'id': self.id,
            'attachment_id': self.attachment_id.id,
            'user_name': self.user_id.name,
            'page_number': self.page_number,
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'note': self.note,
            'color': self.color,
        }
