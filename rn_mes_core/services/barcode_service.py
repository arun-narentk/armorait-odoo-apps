# -*- coding: utf-8 -*-
"""Barcode resolution for shop-floor scans."""

from odoo import models


class RnMesBarcodeService(models.AbstractModel):
    """Match barcodes to work orders, products, employees, machines."""

    _name = 'rn.mes.barcode.service'
    _description = 'MES Barcode Service'

    def process_scan(self, barcode, terminal_id=None, session_id=None):
        barcode = (barcode or '').strip()
        scan_type = 'unknown'
        res_model = False
        res_id = 0

        Workorder = self.env['mrp.workorder']
        wo = Workorder.search([
            ('name', '=', barcode),
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        if wo:
            scan_type, res_model, res_id = 'workorder', 'mrp.workorder', wo.id
        else:
            product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
            if product:
                scan_type, res_model, res_id = 'product', 'product.product', product.id
            else:
                employee = self.env['hr.employee'].search([
                    ('barcode', '=', barcode),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if employee:
                    scan_type, res_model, res_id = 'operator', 'hr.employee', employee.id
                else:
                    device = self.env['rn.mes.machine.device'].search([
                        ('code', '=', barcode),
                        ('company_id', '=', self.env.company.id),
                    ], limit=1)
                    if device:
                        scan_type, res_model, res_id = 'machine', 'rn.mes.machine.device', device.id

        log = self.env['rn.mes.barcode.scan'].create({
            'barcode': barcode,
            'scan_type': scan_type,
            'terminal_id': terminal_id,
            'session_id': session_id,
            'res_model': res_model or '',
            'res_id': res_id,
        })
        return {
            'scan_id': log.id,
            'scan_type': scan_type,
            'res_model': res_model,
            'res_id': res_id,
            'barcode': barcode,
        }
