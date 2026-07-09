# -*- coding: utf-8 -*-
"""Manual / push-API provider."""

from odoo import models


class RnFleetGpsProviderManual(models.AbstractModel):
    _name = 'rn.fleet.gps.provider.manual'
    _inherit = 'rn.fleet.gps.provider.base'
    _description = 'Fleet GPS Manual Provider'

    def test_connection(self, device):
        return {'ok': True, 'message': 'Manual provider ready for API push / wizard ingest'}

    def fetch_latest(self, device):
        # Manual provider relies on ingest endpoint / wizard, not polling
        return False
