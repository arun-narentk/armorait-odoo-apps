# -*- coding: utf-8 -*-
"""Report dataset builders for GSTR summaries."""

from odoo import models


class RnGstReportService(models.AbstractModel):
    """Prepare report data for PDF/Excel/CSV consumers."""

    _name = 'rn.gst.report.service'
    _description = 'GST Report Service'

    def get_return_dataset(self, gst_return):
        """Return a dict dataset describing the return."""
        gst_return.ensure_one()
        return {
            'name': gst_return.name,
            'return_type': gst_return.return_type,
            'period': gst_return.period_id.display_name,
            'totals': {
                'taxable': gst_return.total_taxable,
                'cgst': gst_return.total_cgst,
                'sgst': gst_return.total_sgst,
                'igst': gst_return.total_igst,
                'cess': gst_return.total_cess,
                'tax': gst_return.total_tax,
            },
        }
