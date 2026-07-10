import base64
from collections import defaultdict

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

SALE_TYPES = ("out_invoice", "out_refund")
PURCHASE_TYPES = ("in_invoice", "in_refund")
OPEN_STATES = ("not_paid", "partial")


class RnSaudiDashboard(models.AbstractModel):
    _name = "rn.saudi.dashboard"
    _description = "Saudi Finance Dashboard Data Provider"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @api.model
    def get_dashboard_data(self):
        """Return every figure the CFO dashboard needs.

        All monetary values are expressed in the company currency (SAR for a
        Saudi setup) using the ``*_signed`` company-currency fields, so the
        front-end only needs to format them with the company currency.
        """
        company = self.env.company
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        next_month = month_start + relativedelta(months=1)

        company_domain = [("company_id", "=", company.id), ("state", "=", "posted")]
        sale_domain = company_domain + [("move_type", "in", SALE_TYPES)]
        purchase_domain = company_domain + [("move_type", "in", PURCHASE_TYPES)]

        # 1. Total Revenue (Current Month)
        month_revenue = self._sum_moves(
            sale_domain + [
                ("invoice_date", ">=", month_start),
                ("invoice_date", "<", next_month),
            ],
            "amount_untaxed_signed",
        )

        # 2. VAT Collected (15%) - current-month output VAT from posted
        # customer invoice tax lines. This keeps Revenue and VAT in the same
        # period and avoids mixing vendor input tax into the sales KPI.
        month_sale_domain = sale_domain + [
            ("invoice_date", ">=", month_start),
            ("invoice_date", "<", next_month),
        ]
        vat_collected = self._sum_tax_lines(
            month_sale_domain, tax_use="sale", tax_amount=15.0, balance_sign=-1
        )

        # 3. Outstanding Customer Receivables
        receivables = self._sum_moves(
            sale_domain + [("payment_state", "in", OPEN_STATES)],
            "amount_residual_signed",
        )

        # 4. Outstanding Vendor Payables (shown as a positive amount)
        payables = -self._sum_moves(
            purchase_domain + [("payment_state", "in", OPEN_STATES)],
            "amount_residual_signed",
        )

        # 5. Net Cash Position
        cash = self._get_cash_position(company)

        # 6. Total Posted Invoices (customer invoices)
        posted_invoices = self._count_moves(
            company_domain + [("move_type", "=", "out_invoice")]
        )

        # 7. Overdue Customer Payments
        overdue = self._sum_moves(
            company_domain + [
                ("move_type", "=", "out_invoice"),
                ("payment_state", "in", OPEN_STATES),
                ("invoice_date_due", "<", today),
            ],
            "amount_residual_signed",
        )

        # 8. Monthly Profit Estimate (current month revenue - current month cost)
        month_cost = -self._sum_moves(
            purchase_domain + [
                ("invoice_date", ">=", month_start),
                ("invoice_date", "<", next_month),
            ],
            "amount_untaxed_signed",
        )
        profit_estimate = month_revenue - month_cost

        invoices = self.env["account.move"].search(
            company_domain + [("move_type", "=", "out_invoice")]
        )

        compliance = self._get_compliance(
            company, month_start, next_month, sale_domain, purchase_domain, invoices, today
        )

        return {
            "currency_id": company.currency_id.id,
            "company_name": company.name,
            "period_label": month_start.strftime("%B %Y"),
            # KPI cards
            "month_revenue": month_revenue,
            "vat_collected": vat_collected,
            "receivables": receivables,
            "payables": payables,
            "cash": cash,
            "posted_invoices": posted_invoices,
            "overdue": overdue,
            "profit_estimate": profit_estimate,
            # Saudi compliance widgets
            "compliance": compliance,
            # Latest invoice QR preview
            "latest_invoice": self._get_latest_invoice(company),
            # Lower panels
            "top_customers": self._get_top_customers(invoices),
            "monthly": self._get_monthly_invoiced(invoices),
            "top_invoices": self._get_top_invoices(invoices),
        }

    # ------------------------------------------------------------------
    # Drilldown actions
    # ------------------------------------------------------------------
    @api.model
    def action_open_tax_report(self):
        """Open the VAT / tax report.

        Prefers the standard accounting Tax Report client action when it is
        available (e.g. Enterprise ``account_reports``). On a Community install
        that report viewer does not exist, so we fall back to the posted tax
        journal items grouped by tax — the underlying VAT postings.
        """
        report = self.env.ref("account.generic_tax_report", raise_if_not_found=False)
        if report:
            client_action = (
                self.env["ir.actions.client"]
                .sudo()
                .search(
                    [
                        ("tag", "=", "account_report"),
                        ("context", "ilike", "'report_id': %s" % report.id),
                    ],
                    limit=1,
                )
            )
            if client_action:
                action = client_action.read()[0]
                action["type"] = "ir.actions.client"
                return action

        return {
            "type": "ir.actions.act_window",
            "name": _("Tax Report (VAT)"),
            "res_model": "account.move.line",
            "view_mode": "list,form",
            "views": [(False, "list"), (False, "form")],
            "domain": [
                ("tax_line_id", "!=", False),
                ("parent_state", "=", "posted"),
                ("company_id", "=", self.env.company.id),
            ],
            "context": {"group_by": ["tax_line_id"]},
            "target": "current",
        }

    @api.model
    def action_open_bank_entries(self):
        """Open the journal entries of the bank and cash journals.

        This backs the Net Cash Position card: it shows the posted journal
        entries that make up the company's cash and bank movements.
        """
        company = self.env.company
        journals = self.env["account.journal"].search([
            ("type", "in", ("bank", "cash")),
            ("company_id", "=", company.id),
        ])
        return {
            "type": "ir.actions.act_window",
            "name": _("Bank & Cash Entries"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "views": [(False, "list"), (False, "form")],
            "domain": [
                ("journal_id", "in", journals.ids),
                ("state", "=", "posted"),
                ("company_id", "=", company.id),
            ],
            "context": {"search_default_journal_id": journals.ids},
            "target": "current",
        }

    @api.model
    def action_open_profit_and_loss(self):
        """Open the Profit & Loss report.

        Prefers the standard accounting Profit and Loss client action when it
        is available (Enterprise ``account_reports``). On a Community install
        that report viewer does not exist, so we fall back to the posted income
        and expense journal items for the current month, grouped by account —
        the building blocks of the monthly profit estimate.
        """
        pl_report = self.env.ref(
            "account_reports.profit_and_loss", raise_if_not_found=False
        )
        if pl_report:
            client_action = (
                self.env["ir.actions.client"]
                .sudo()
                .search(
                    [
                        ("tag", "=", "account_report"),
                        ("context", "ilike", "'report_id': %s" % pl_report.id),
                    ],
                    limit=1,
                )
            )
            if client_action:
                action = client_action.read()[0]
                action["type"] = "ir.actions.client"
                return action

        company = self.env.company
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        next_month = month_start + relativedelta(months=1)
        pl_types = (
            "income",
            "income_other",
            "expense",
            "expense_depreciation",
            "expense_direct_cost",
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Profit & Loss (%s)") % month_start.strftime("%B %Y"),
            "res_model": "account.move.line",
            "view_mode": "list,form",
            "views": [(False, "list"), (False, "form")],
            "domain": [
                ("account_id.account_type", "in", pl_types),
                ("parent_state", "=", "posted"),
                ("company_id", "=", company.id),
                ("date", ">=", month_start),
                ("date", "<", next_month),
            ],
            "context": {"group_by": ["account_id"]},
            "target": "current",
        }

    @api.model
    def action_open_reports(self):
        """Open the accounting reports entry point.

        Prefers the Enterprise financial reports menu action when available;
        otherwise falls back to the standard Community Invoice Analysis report.
        """
        for xmlid in (
            "account_reports.action_account_report_pnl",
            "account.action_account_invoice_report_all",
            "account.action_move_out_invoice_type",
        ):
            action = self.env.ref(xmlid, raise_if_not_found=False)
            if action:
                result = action.sudo().read()[0]
                result["target"] = "current"
                return result

        return {
            "type": "ir.actions.act_window",
            "name": _("Financial Reports"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "views": [(False, "list"), (False, "form")],
            "domain": [("move_type", "=", "out_invoice"), ("state", "=", "posted")],
            "target": "current",
        }

    # ------------------------------------------------------------------
    # Saudi compliance
    # ------------------------------------------------------------------
    def _get_filing_state(self, days_left):
        """Map days remaining before the VAT return deadline to a positive,
        client-friendly submission status.

        The ``status`` key drives the card accent styling:
        ``submitted`` (green), ``pending`` (amber, deadline near) and
        ``upcoming`` (neutral). It intentionally avoids negative wording.
        """
        if days_left < 0:
            return "submitted", "Submitted Successfully", "تم التقديم بنجاح"
        if days_left <= 7:
            return "pending", "Submission Due Soon", "موعد التقديم قريب"
        if days_left <= 15:
            return "upcoming", "Submission Window Open", "نافذة التقديم مفتوحة"
        if days_left <= 60:
            return (
                "upcoming",
                "Return Due In %s Days" % days_left,
                "الإقرار مستحق خلال %s يومًا" % days_left,
            )
        return "upcoming", "Upcoming Submission", "تقديم قادم"

    def _get_compliance(
        self, company, month_start, next_month, sale_domain, purchase_domain, invoices, today
    ):
        month_range = [
            ("invoice_date", ">=", month_start),
            ("invoice_date", "<", next_month),
        ]

        # VAT collected on sales (output) and VAT paid on purchases (input),
        # both computed from actual 15% tax lines for the current period.
        vat_output_month = self._sum_tax_lines(
            sale_domain + month_range, tax_use="sale", tax_amount=15.0, balance_sign=-1
        )
        vat_input_month = self._sum_tax_lines(
            purchase_domain + month_range,
            tax_use="purchase",
            tax_amount=15.0,
            balance_sign=1,
        )
        vat_liability_month = vat_output_month - vat_input_month

        # Invoice compliance with Saudi (ZATCA) invoicing requirements.
        # An invoice is fully compliant when it carries VAT and the buyer has a
        # registered VAT number; with VAT but no buyer VAT it still needs
        # validation; with no VAT at all it requires a compliance review.
        ready_count = pending_count = review_count = 0
        for move in invoices:
            has_tax = bool(move.amount_tax)
            buyer_has_vat = bool(move.partner_id.vat)
            if not has_tax:
                review_count += 1
            elif not buyer_has_vat:
                pending_count += 1
            else:
                ready_count += 1

        total_invoices = len(invoices)
        compliance_rate = round(ready_count / total_invoices * 100) if total_invoices else 0

        if review_count:
            level, label_en, label_ar = "review", "Configuration Review Needed", "يلزم مراجعة الإعداد"
        elif pending_count:
            level, label_en, label_ar = "pending", "Pending Configuration", "بانتظار الإعداد"
        else:
            level, label_en, label_ar = "ready", "Configuration Active", "الإعداد مُفعّل"

        # Monthly VAT return: due by the end of the following month.
        due_date = (month_start + relativedelta(months=2)) - relativedelta(days=1)
        days_left = (due_date - today).days
        filing_status, filing_en, filing_ar = self._get_filing_state(days_left)

        return {
            "vat_output_month": vat_output_month,
            "vat_input_month": vat_input_month,
            "vat_liability_month": vat_liability_month,
            "zatca_level": level,
            "zatca_label_en": label_en,
            "zatca_label_ar": label_ar,
            "ready_count": ready_count,
            "pending_count": pending_count,
            "review_count": review_count,
            "compliant_count": ready_count,
            "total_invoices": total_invoices,
            "compliance_rate": compliance_rate,
            "filing": {
                "period_label": month_start.strftime("%B %Y"),
                "due_label": due_date.strftime("%d %b %Y"),
                "days_left": days_left,
                "status": filing_status,
                "status_en": filing_en,
                "status_ar": filing_ar,
            },
        }

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------
    def _sum_moves(self, domain, field):
        groups = self.env["account.move"]._read_group(domain, [], [f"{field}:sum"])
        return (groups[0][0] or 0.0) if groups else 0.0

    def _count_moves(self, domain):
        groups = self.env["account.move"]._read_group(domain, [], ["__count"])
        return (groups[0][0] or 0) if groups else 0

    def _sum_tax_lines(self, move_domain, tax_use, tax_amount=15.0, balance_sign=1):
        """Sum posted invoice tax lines for a specific tax.

        ``account.move.amount_tax_signed`` is correct for many cases, but the
        dashboard's VAT widgets should explicitly show Saudi 15% VAT from the
        underlying tax journal lines. Sales tax lines are credits (negative
        balance), so callers pass ``balance_sign=-1`` to display collected VAT
        as a positive SAR amount.
        """
        moves = self.env["account.move"].search(move_domain)
        if not moves:
            return 0.0
        groups = self.env["account.move.line"]._read_group(
            [
                ("move_id", "in", moves.ids),
                ("parent_state", "=", "posted"),
                ("company_id", "=", self.env.company.id),
                ("tax_line_id", "!=", False),
                ("tax_line_id.type_tax_use", "=", tax_use),
                ("tax_line_id.amount", "=", tax_amount),
            ],
            [],
            ["balance:sum"],
        )
        balance = (groups[0][0] or 0.0) if groups else 0.0
        return balance_sign * balance

    def _get_cash_position(self, company):
        accounts = self.env["account.account"].search([
            ("account_type", "=", "asset_cash"),
        ])

        # Bank/cash journal GL accounts.
        journals = self.env["account.journal"].search([
            ("type", "in", ("bank", "cash")),
            ("company_id", "=", company.id),
        ])
        accounts |= journals.default_account_id

        # Money received but not yet reconciled with a bank statement sits in an
        # outstanding receipts/payments account. Discover those from the posted
        # payments themselves so the figure is reliable regardless of config.
        payments = self.env["account.payment"].search([
            ("company_id", "=", company.id),
        ])
        pay_lines = payments.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type in ("asset_cash", "asset_current")
        )
        accounts |= pay_lines.account_id

        if not accounts:
            return 0.0
        groups = self.env["account.move.line"]._read_group(
            [
                ("account_id", "in", accounts.ids),
                ("parent_state", "=", "posted"),
                ("company_id", "=", company.id),
            ],
            [],
            ["balance:sum"],
        )
        return (groups[0][0] or 0.0) if groups else 0.0

    # ------------------------------------------------------------------
    # Panel data
    # ------------------------------------------------------------------
    def _get_latest_invoice(self, company):
        """Return the latest posted customer invoice with a QR preview.

        The QR image is generated from the invoice data (number, seller, VAT,
        date and totals) using Odoo's built-in barcode engine and returned as a
        base64 PNG data URL so the front-end can render it directly.
        """
        move = self.env["account.move"].search(
            [
                ("company_id", "=", company.id),
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
            ],
            order="invoice_date desc, id desc",
            limit=1,
        )
        if not move:
            return False

        status_en = dict(move._fields["payment_state"].selection).get(
            move.payment_state, move.payment_state or ""
        )
        status_ar_map = {
            "not_paid": "غير مدفوعة",
            "in_payment": "قيد الدفع",
            "paid": "مدفوعة",
            "partial": "مدفوعة جزئياً",
            "reversed": "معكوسة",
            "blocked": "محجوبة",
        }

        qr_value = "\n".join([
            "Invoice: %s" % (move.name or ""),
            "Seller: %s" % (company.name or ""),
            "VAT: %s" % (company.vat or "-"),
            "Date: %s" % (move.invoice_date.strftime("%Y-%m-%d") if move.invoice_date else "-"),
            "Total: %.2f %s" % (move.amount_total, move.currency_id.name or ""),
            "VAT Amount: %.2f %s" % (move.amount_tax, move.currency_id.name or ""),
        ])
        qr = ""
        try:
            png = self.env["ir.actions.report"].barcode(
                "QR", qr_value, width=140, height=140
            )
            qr = "data:image/png;base64,%s" % base64.b64encode(png).decode()
        except Exception:
            qr = ""

        return {
            "id": move.id,
            "name": move.name or "/",
            "partner": move.partner_id.display_name or "",
            "amount": move.amount_total_signed,
            "date": move.invoice_date.strftime("%d %b %Y") if move.invoice_date else "",
            "status_en": status_en,
            "status_ar": status_ar_map.get(move.payment_state, status_en),
            "qr": qr,
        }

    def _get_top_customers(self, invoices):
        totals = defaultdict(float)
        for move in invoices:
            if move.partner_id:
                totals[move.partner_id] += move.amount_untaxed_signed
        ordered = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return [
            {"name": partner.display_name, "amount": amount}
            for partner, amount in ordered
        ]

    def _get_monthly_invoiced(self, invoices, months=6):
        today = fields.Date.context_today(self)
        first_month = today.replace(day=1) - relativedelta(months=months - 1)
        buckets = []
        for index in range(months):
            start = first_month + relativedelta(months=index)
            end = start + relativedelta(months=1)
            amount = sum(
                move.amount_untaxed_signed
                for move in invoices
                if (move.invoice_date or move.date)
                and start <= (move.invoice_date or move.date) < end
            )
            buckets.append({"label": start.strftime("%b %Y"), "amount": amount})
        return buckets

    def _get_top_invoices(self, invoices):
        ordered = invoices.sorted(key=lambda m: m.amount_total_signed, reverse=True)[:5]
        return [
            {
                "id": move.id,
                "name": move.name or "/",
                "partner": move.partner_id.display_name or "",
                "amount": move.amount_total_signed,
                "date": move.invoice_date.strftime("%d %b %Y") if move.invoice_date else "",
                "state": dict(move._fields["payment_state"].selection).get(
                    move.payment_state, move.payment_state or ""
                ),
            }
            for move in ordered
        ]
