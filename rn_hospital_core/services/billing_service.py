# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError


class RnHospitalBillingService(models.AbstractModel):
    _name = 'rn.hospital.billing.service'
    _description = 'Hospital Billing Service'

    def create_charge(self, patient_id, charge_type, description, unit_price, quantity=1.0, **links):
        patient = self.env['rn.hospital.patient'].browse(patient_id)
        if not patient.exists():
            raise UserError('Patient not found.')
        return self.env['rn.hospital.billing.line'].create({
            'patient_id': patient.id,
            'charge_type': charge_type,
            'description': description,
            'unit_price': unit_price,
            'quantity': quantity,
            'appointment_id': links.get('appointment_id'),
            'admission_id': links.get('admission_id'),
            'encounter_id': links.get('encounter_id'),
        }).id

    def generate_invoice(self, patient_id, line_ids=None):
        patient = self.env['rn.hospital.patient'].browse(patient_id)
        domain = [('patient_id', '=', patient.id), ('state', '=', 'draft')]
        if line_ids:
            domain.append(('id', 'in', line_ids))
        lines = self.env['rn.hospital.billing.line'].search(domain)
        if not lines:
            raise UserError('No draft billing lines found.')
        partner = patient.partner_id or self.env['res.partner'].create({'name': patient.name})
        if not patient.partner_id:
            patient.partner_id = partner.id
        invoice_lines = []
        for line in lines:
            invoice_lines.append((0, 0, {
                'name': line.description,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
                'product_id': line.product_id.id if line.product_id else False,
            }))
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': invoice_lines,
        })
        lines.write({'invoice_id': invoice.id, 'state': 'invoiced'})
        return invoice.id
