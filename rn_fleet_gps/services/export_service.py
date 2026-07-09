# -*- coding: utf-8 -*-
"""CSV exports."""

import base64

from odoo import fields, models


class RnFleetExportService(models.AbstractModel):
    _name = 'rn.fleet.export.service'
    _description = 'Fleet Export Service'

    def export_trips_csv(self, company_id=None, limit=500):
        company_id = company_id or self.env.company.id
        trips = self.env['rn.fleet.trip'].search([('company_id', '=', company_id)], limit=limit)
        lines = ['name,vehicle,driver,start,end,distance_km,state']
        for t in trips:
            lines.append('%s,%s,%s,%s,%s,%s,%s' % (
                t.name,
                (t.vehicle_id.name or '').replace(',', ' '),
                (t.driver_id.name or '').replace(',', ' '),
                fields.Datetime.to_string(t.date_start) if t.date_start else '',
                fields.Datetime.to_string(t.date_end) if t.date_end else '',
                t.distance_km or 0.0,
                t.state,
            ))
        content = chr(10).join(lines)
        att = self.env['ir.attachment'].create({
            'name': 'fleet_trips.csv',
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % att.id,
            'target': 'self',
        }
