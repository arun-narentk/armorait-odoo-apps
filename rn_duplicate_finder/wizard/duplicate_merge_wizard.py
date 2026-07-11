# -*- coding: utf-8 -*-
"""Merge duplicate records from scan results."""

from odoo import api, fields, models


class RnDupMergeWizard(models.TransientModel):
    _name = 'rn.dup.merge.wizard'
    _description = 'Duplicate Merge Wizard'

    result_id = fields.Many2one('rn.dup.result', required=True)
    model_name = fields.Char(required=True)
    master_res_id = fields.Integer(required=True, string='Keep Record')
    duplicate_res_id = fields.Integer(required=True, string='Merge Record')
    master_ref = fields.Reference(
        selection='_selection_target_model',
        string='Master Record',
        compute='_compute_refs',
    )
    duplicate_ref = fields.Reference(
        selection='_selection_target_model',
        string='Duplicate Record',
        compute='_compute_refs',
    )

    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    @api.depends('model_name', 'master_res_id', 'duplicate_res_id')
    def _compute_refs(self):
        for wizard in self:
            wizard.master_ref = (
                f'{wizard.model_name},{wizard.master_res_id}'
                if wizard.model_name and wizard.master_res_id
                else False
            )
            wizard.duplicate_ref = (
                f'{wizard.model_name},{wizard.duplicate_res_id}'
                if wizard.model_name and wizard.duplicate_res_id
                else False
            )

    def action_merge(self):
        self.ensure_one()
        master = self.env['rn.dup.merge.service'].merge_records(
            self.model_name,
            self.master_res_id,
            self.duplicate_res_id,
            result=self.result_id,
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.model_name,
            'view_mode': 'form',
            'res_id': master.id,
        }
