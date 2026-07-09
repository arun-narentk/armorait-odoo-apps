# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetSurgery(models.Model):
    _name = 'rn.vet.surgery'
    _description = 'Pet Surgery'
    _inherit = ['mail.thread']
    _order = 'surgery_date desc'

    name = fields.Char(required=True)
    pet_id = fields.Many2one('rn.vet.pet', required=True, index=True)
    surgeon_id = fields.Many2one('hr.employee', string='Surgeon', required=True)
    surgery_date = fields.Datetime(required=True)
    procedure = fields.Char(required=True)
    anaesthesia_note = fields.Text()
    recovery_note = fields.Text()
    state = fields.Selection(
        [('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='scheduled',
        tracking=True,
    )
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)
