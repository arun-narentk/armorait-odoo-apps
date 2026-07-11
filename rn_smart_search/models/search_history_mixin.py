# -*- coding: utf-8 -*-

from odoo import models


class RnSearchHistoryMixin(models.AbstractModel):
    _name = 'rn.search.history.mixin'
    _description = 'Smart Search History Mixin'

    def smart_search_track_view(self):
        """Log a viewed record for the current user."""
        self.ensure_one()
        return self.env['rn.smart.search.service'].log_view(
            self._name,
            self.id,
            self.display_name,
        )
