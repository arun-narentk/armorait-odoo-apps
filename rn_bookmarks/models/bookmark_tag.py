# -*- coding: utf-8 -*-
from odoo import fields, models

from .. import constants as bm_constants


class BookmarkTag(models.Model):
    _name = 'rn.bookmark.tag'
    _description = 'Bookmark Tag'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Selection(bm_constants.BOOKMARK_COLORS, default='gray')
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    active = fields.Boolean(default=True)
