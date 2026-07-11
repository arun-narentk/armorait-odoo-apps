# -*- coding: utf-8 -*-
"""Duplicate scan runs."""

from odoo import fields, models


class RnDupScan(models.Model):
    _name = 'rn.dup.scan'
    _description = 'Duplicate Scan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scan_date desc, id desc'

    name = fields.Char(required=True, copy=False, default='New')
    rule_id = fields.Many2one('rn.dup.rule', required=True, ondelete='restrict', index=True)
    model_name = fields.Char(related='rule_id.model_name', store=True, readonly=True)
    company_id = fields.Many2one(
        'res.company',
        related='rule_id.company_id',
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Done'),
            ('failed', 'Failed'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    scan_date = fields.Datetime(default=fields.Datetime.now, required=True)
    record_count = fields.Integer(readonly=True)
    match_count = fields.Integer(readonly=True)
    result_ids = fields.One2many('rn.dup.result', 'scan_id', string='Matches')
    error_message = fields.Text(readonly=True)

    def action_open_results(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Duplicate Results',
            'res_model': 'rn.dup.result',
            'view_mode': 'list,form',
            'domain': [('scan_id', '=', self.id)],
            'context': {'default_scan_id': self.id},
        }

    def action_ignore_all_new(self):
        for scan in self:
            scan.result_ids.filtered(lambda r: r.state == 'new').action_ignore_pair()
