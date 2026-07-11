# -*- coding: utf-8 -*-
"""Duplicate match results."""

from odoo import api, fields, models


class RnDupResult(models.Model):
    _name = 'rn.dup.result'
    _description = 'Duplicate Result'
    _order = 'score desc, id desc'

    scan_id = fields.Many2one('rn.dup.scan', required=True, ondelete='cascade', index=True)
    rule_id = fields.Many2one(related='scan_id.rule_id', store=True, readonly=True)
    company_id = fields.Many2one(related='scan_id.company_id', store=True, readonly=True)
    model_name = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, string='Record ID', index=True)
    duplicate_res_id = fields.Integer(required=True, string='Duplicate Record ID', index=True)
    record_ref = fields.Reference(
        selection='_selection_target_model',
        string='Record',
        compute='_compute_record_refs',
        store=True,
    )
    duplicate_ref = fields.Reference(
        selection='_selection_target_model',
        string='Duplicate',
        compute='_compute_record_refs',
        store=True,
    )
    score = fields.Float(digits=(5, 2), required=True)
    match_summary = fields.Char()
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('ignored', 'Ignored'),
            ('merged', 'Merged'),
        ],
        default='new',
        required=True,
        index=True,
    )

    _sql_constraints = [
        (
            'uniq_pair_per_scan',
            'unique(scan_id, model_name, res_id, duplicate_res_id)',
            'This duplicate pair already exists on the scan.',
        ),
    ]

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    @api.depends('model_name', 'res_id', 'duplicate_res_id')
    def _compute_record_refs(self):
        for result in self:
            result.record_ref = (
                f'{result.model_name},{result.res_id}'
                if result.model_name and result.res_id
                else False
            )
            result.duplicate_ref = (
                f'{result.model_name},{result.duplicate_res_id}'
                if result.model_name and result.duplicate_res_id
                else False
            )

    def action_ignore_pair(self):
        Ignore = self.env['rn.dup.ignore']
        for result in self:
            if result.state == 'merged':
                continue
            Ignore._register_ignore(
                result.rule_id,
                result.model_name,
                result.res_id,
                result.duplicate_res_id,
            )
            result.state = 'ignored'

    def action_open_merge_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Merge Duplicates',
            'res_model': 'rn.dup.merge.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_result_id': self.id,
                'default_model_name': self.model_name,
                'default_master_res_id': self.res_id,
                'default_duplicate_res_id': self.duplicate_res_id,
            },
        }
