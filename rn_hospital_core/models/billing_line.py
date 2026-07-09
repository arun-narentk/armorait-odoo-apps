# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHospitalBillingLine(models.Model):
    """Hospital charge line linked to patient and invoice."""

    _name = 'rn.hospital.billing.line'
    _description = 'Hospital Billing Line'
    _order = 'charge_date desc'

    patient_id = fields.Many2one('rn.hospital.patient', required=True, index=True)
    appointment_id = fields.Many2one('rn.hospital.appointment')
    admission_id = fields.Many2one('rn.hospital.admission')
    encounter_id = fields.Many2one('rn.hospital.emr.encounter')
    charge_type = fields.Selection(
        [
            ('consultation', 'Consultation'),
            ('pharmacy', 'Pharmacy'),
            ('lab', 'Laboratory'),
            ('radiology', 'Radiology'),
            ('ot', 'Operation Theatre'),
            ('room', 'Room Charge'),
            ('package', 'Package'),
            ('other', 'Other'),
        ],
        required=True,
        default='consultation',
    )
    description = fields.Char(required=True)
    product_id = fields.Many2one('product.product')
    quantity = fields.Float(default=1.0)
    unit_price = fields.Float(required=True)
    amount = fields.Float(compute='_compute_amount', store=True)
    charge_date = fields.Datetime(default=fields.Datetime.now)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('invoiced', 'Invoiced'), ('paid', 'Paid')],
        default='draft',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.amount = (line.quantity or 0.0) * (line.unit_price or 0.0)
