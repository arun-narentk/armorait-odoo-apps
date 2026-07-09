# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnVetAppointment(models.Model):
    _name = 'rn.vet.appointment'
    _description = 'Vet Appointment'
    _inherit = ['mail.thread']
    _order = 'start_datetime desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    pet_id = fields.Many2one('rn.vet.pet', required=True, index=True)
    owner_id = fields.Many2one(related='pet_id.owner_id', store=True, index=True)
    veterinarian_id = fields.Many2one('hr.employee', string='Veterinarian', required=True, index=True)
    appointment_type = fields.Selection(
        [
            ('consultation', 'Consultation'),
            ('vaccination', 'Vaccination'),
            ('surgery', 'Surgery'),
            ('grooming', 'Grooming'),
            ('boarding', 'Boarding'),
            ('emergency', 'Emergency'),
        ],
        default='consultation',
        required=True,
    )
    start_datetime = fields.Datetime(required=True, index=True)
    end_datetime = fields.Datetime()
    duration_minutes = fields.Integer(default=30)
    state = fields.Selection(
        [
            ('scheduled', 'Scheduled'),
            ('checked_in', 'Checked In'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='scheduled',
        tracking=True,
    )
    reason = fields.Text()
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.vet.appointment') or 'VAP'
        return super().create(vals_list)

    def action_check_in(self):
        self.write({'state': 'checked_in'})

    def action_complete(self):
        self.write({'state': 'completed'})
