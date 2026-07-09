# -*- coding: utf-8 -*-
"""Barcode scan wizard for backend testing."""

from odoo import fields, models


class RnMesBarcodeScanWizard(models.TransientModel):
    _name = 'rn.mes.barcode.scan.wizard'
    _description = 'MES Barcode Scan Wizard'

    barcode = fields.Char(required=True)
    terminal_id = fields.Many2one('rn.mes.terminal')
    session_id = fields.Many2one('rn.mes.production.session')
    result_message = fields.Text(readonly=True)

    def action_process(self):
        self.ensure_one()
        result = self.env['rn.mes.barcode.service'].process_scan(
            self.barcode,
            terminal_id=self.terminal_id.id,
            session_id=self.session_id.id,
        )
        self.result_message = (
            f"Type: {result['scan_type']}\n"
            f"Model: {result['res_model']}\n"
            f"Record ID: {result['res_id']}"
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
