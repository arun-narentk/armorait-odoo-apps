# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalLabService(models.AbstractModel):
    _name = 'rn.dental.lab.service'
    _description = 'Lab Workflow Service'

    def send_to_lab(self, request_id):
        req = self.env['rn.dental.lab.request'].browse(request_id)
        req.write({'state': 'sent'})
        return True

    def mark_ready(self, request_id):
        req = self.env['rn.dental.lab.request'].browse(request_id)
        req.write({'state': 'ready', 'received_date': fields.Date.context_today(self)})
        return True

    def deliver_to_patient(self, request_id):
        req = self.env['rn.dental.lab.request'].browse(request_id)
        req.write({'state': 'delivered'})
        return True
