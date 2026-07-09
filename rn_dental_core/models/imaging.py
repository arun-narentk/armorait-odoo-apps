# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalImaging(models.Model):
    _name = 'rn.dental.imaging'
    _description = 'Dental Imaging'
    _order = 'capture_date desc'

    name = fields.Char(required=True)
    patient_id = fields.Many2one('rn.dental.patient', required=True, ondelete='cascade', index=True)
    image_type = fields.Selection(
        [
            ('xray', 'X-Ray'),
            ('cbct', 'CBCT'),
            ('intraoral', 'Intraoral Photo'),
            ('scan', 'Scan'),
            ('document', 'Document'),
        ],
        default='xray',
        required=True,
    )
    capture_date = fields.Date(default=fields.Date.context_today, required=True)
    tooth_number = fields.Char()
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    note = fields.Text()
    company_id = fields.Many2one(related='patient_id.company_id', store=True, index=True)
