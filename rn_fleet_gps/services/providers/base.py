# -*- coding: utf-8 -*-
"""Abstract GPS provider interface."""

from odoo import models


class RnFleetGpsProviderBase(models.AbstractModel):
    _name = 'rn.fleet.gps.provider.base'
    _description = 'Fleet GPS Provider Base'

    def test_connection(self, device):
        return {'ok': False, 'message': 'Not implemented'}

    def fetch_latest(self, device):
        """Return normalized location dict or False."""
        return False

    def normalize_payload(self, payload):
        return payload or {}
