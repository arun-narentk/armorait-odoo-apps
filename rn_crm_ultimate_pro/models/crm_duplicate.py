# -*- coding: utf-8 -*-
"""Duplicate lead detection batches and match lines."""

from odoo import fields, models


class RnCrmDuplicateBatch(models.Model):
    """A scan run that groups possible duplicate leads."""

    _name = 'rn.crm.duplicate.batch'
    _description = 'CRM Duplicate Batch'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(required=True, default='Duplicate Scan')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    sensitivity = fields.Selection(
        selection=[('strict', 'Strict'), ('balanced', 'Balanced'), ('loose', 'Loose')],
        default='balanced',
    )
    match_count = fields.Integer()
    line_ids = fields.One2many('rn.crm.duplicate.line', 'batch_id', string='Matches')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)


class RnCrmDuplicateLine(models.Model):
    """One duplicate suggestion between two leads."""

    _name = 'rn.crm.duplicate.line'
    _description = 'CRM Duplicate Line'
    _order = 'confidence desc, id'

    batch_id = fields.Many2one('rn.crm.duplicate.batch', required=True, ondelete='cascade', index=True)
    lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade')
    duplicate_lead_id = fields.Many2one('crm.lead', required=True, ondelete='cascade')
    match_on = fields.Char(help='email,phone,company,gstin,...')
    confidence = fields.Float(digits=(16, 2))
    state = fields.Selection(
        selection=[('suggested', 'Suggested'), ('merged', 'Merged'), ('ignored', 'Ignored')],
        default='suggested',
    )
    company_id = fields.Many2one(related='batch_id.company_id', store=True)
