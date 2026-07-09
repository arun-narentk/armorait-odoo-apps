# -*- coding: utf-8 -*-
"""Customer support tickets from the experience portal."""

from odoo import api, fields, models


class RnCustomerExperienceTicket(models.Model):
    _name = 'rn.customer.experience.ticket'
    _description = 'Experience Support Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(copy=False, index=True, default='New')
    partner_id = fields.Many2one('res.partner', required=True, index=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    description = fields.Text(required=True)
    category = fields.Selection(
        selection=[
            ('service', 'Service'),
            ('warranty', 'Warranty'),
            ('billing', 'Billing'),
            ('delivery', 'Delivery'),
            ('other', 'Other'),
        ],
        default='service',
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Urgent'),
        ],
        default='1',
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('waiting', 'Waiting Customer'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        default='new',
        tracking=True,
    )
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    ai_category = fields.Char(string='AI Category')
    ai_suggestion = fields.Text(string='AI Suggestion')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'rn.customer.experience.ticket'
                ) or 'New'
        return super().create(vals_list)
