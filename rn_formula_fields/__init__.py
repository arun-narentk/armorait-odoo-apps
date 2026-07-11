# -*- coding: utf-8 -*-

from . import models
from . import services
from . import wizard


def post_init_hook(env):
    """Synchronise dynamic fields after module data is loaded."""
    env['rn.formula.field'].sudo().search([])._sync_ir_field()
