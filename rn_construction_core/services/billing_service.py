# -*- coding: utf-8 -*-

from odoo import models


class RnConstructionBillingService(models.AbstractModel):
    _name = 'rn.construction.billing.service'
    _description = 'Billing Service'

    def submit_running_bill(self, bill_id):
        bill = self.env['rn.construction.running.bill'].browse(bill_id)
        bill.write({'state': 'submitted'})
        return True

    def approve_running_bill(self, bill_id):
        bill = self.env['rn.construction.running.bill'].browse(bill_id)
        bill.write({'state': 'approved'})
        return True

    def create_client_invoice(self, bill_id):
        bill = self.env['rn.construction.running.bill'].browse(bill_id)
        bill.ensure_one()
        project = bill.construction_project_id
        partner = project.client_id or self.env.ref('base.res_partner_1', raise_if_not_found=False)
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id if partner else False,
            'invoice_line_ids': [(0, 0, {
                'name': f'Running bill {bill.name}',
                'quantity': 1,
                'price_unit': bill.net_payable,
            })],
        })
        bill.write({'state': 'invoiced', 'invoice_id': move.id})
        return move.id
