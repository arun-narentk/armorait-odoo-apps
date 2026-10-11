# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Point the noupdate cleanup cron at rn.search.history on old installs."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    cron = env.ref('rn_smart_search.ir_cron_rn_smart_search_cleanup', raise_if_not_found=False)
    if not cron:
        return
    cron.write({
        'model_id': env.ref('rn_smart_search.model_rn_search_history').id,
        'code': 'model._cron_cleanup_stale_history()',
    })
