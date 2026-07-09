# -*- coding: utf-8 -*-
"""Authenticated customer sessions for AI engagement."""

from odoo import fields, models


class RnCustomerEngagementSession(models.Model):
    _name = 'rn.customer.engagement.session'
    _description = 'Customer Engagement Session'
    _order = 'create_date desc'

    name = fields.Char(required=True, copy=False, default='New')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channel_id = fields.Many2one('rn.customer.engagement.channel', required=True, ondelete='restrict')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    auth_state = fields.Selection([('pending', 'Pending'), ('authenticated', 'Authenticated'), ('expired', 'Expired')], default='pending', required=True)
    external_contact = fields.Char(required=True, index=True)
    auth_reference = fields.Char()
    expires_at = fields.Datetime()
