# -*- coding: utf-8 -*-
"""Prepare mobile framework metadata outputs."""

from odoo import models


class RnMobileBuilderService(models.AbstractModel):
    _name = 'rn.mobile.builder.service'
    _description = 'Mobile Builder Service'

    def build_metadata(self, app):
        return {
            'app': {
                'name': app.name,
                'scope': app.app_scope,
                'target_model': app.target_model,
                'features': {
                    'offline': app.enable_offline,
                    'barcode': app.enable_barcode,
                    'camera': app.enable_camera,
                    'gps': app.enable_gps,
                    'push': app.enable_push,
                    'signature': app.enable_signature,
                },
            },
            'screens': [{
                'name': screen.name,
                'type': screen.screen_type,
                'model': screen.model_name,
                'offline': screen.offline_enabled,
            } for screen in app.mapped('screen_ids')],
            'sync_profiles': [{
                'model': profile.model_name,
                'mode': profile.sync_mode,
                'limit': profile.offline_limit,
                'conflict': profile.conflict_strategy,
            } for profile in app.mapped('sync_profile_ids')],
        }
