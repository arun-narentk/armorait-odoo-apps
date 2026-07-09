# -*- coding: utf-8 -*-
"""Provider registry."""

from odoo import models


class RnFleetGpsProviderService(models.AbstractModel):
    _name = 'rn.fleet.gps.provider.service'
    _description = 'Fleet GPS Provider Service'

    REGISTRY = {
        'manual': 'rn.fleet.gps.provider.manual',
        'traccar': 'rn.fleet.gps.provider.traccar',
        'teltonika': 'rn.fleet.gps.provider.manual',
        'gt06': 'rn.fleet.gps.provider.manual',
        'wialon': 'rn.fleet.gps.provider.manual',
        'ruptela': 'rn.fleet.gps.provider.manual',
        'tk103': 'rn.fleet.gps.provider.manual',
        'other': 'rn.fleet.gps.provider.manual',
    }

    def get_provider(self, device):
        device.ensure_one()
        return self.env[self.REGISTRY.get(device.provider, 'rn.fleet.gps.provider.manual')]

    def test_connection(self, device):
        return self.get_provider(device).test_connection(device)

    def fetch_latest(self, device):
        return self.get_provider(device).fetch_latest(device)
