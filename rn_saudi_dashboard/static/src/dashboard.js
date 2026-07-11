import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { Component, onWillStart, useState } from "@odoo/owl";

export class SaudiDashboard extends Component {
    static template = "rn_saudi_dashboard.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        // `lang` drives the bilingual labels and RTL layout ("en" | "ar").
        // `tip` powers the custom Arabic hover tooltip (no browser title attr).
        this.state = useState({
            loading: true,
            data: {},
            lang: "en",
            tip: { visible: false, en: "", ar: "", x: 0, y: 0 },
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    get isRTL() {
        return this.state.lang === "ar";
    }

    toggleLang() {
        this.state.lang = this.state.lang === "ar" ? "en" : "ar";
    }

    async loadData() {
        this.state.loading = true;
        this.state.data = await this.orm.call("rn.saudi.dashboard", "get_dashboard_data", []);
        this.state.loading = false;
    }

    formatCurrency(value) {
        return formatMonetary(value || 0, { currencyId: this.state.data.currency_id });
    }

    get maxMonthly() {
        const months = this.state.data.monthly || [];
        return Math.max(1, ...months.map((m) => Math.abs(m.amount)));
    }

    barWidth(amount) {
        const pct = Math.round((Math.abs(amount) / this.maxMonthly) * 100);
        return `${Math.max(pct, 2)}%`;
    }

    // --- Compliance helpers ----------------------------------------------
    get compliance() {
        return this.state.data.compliance || {};
    }

    get latestInvoice() {
        return this.state.data.latest_invoice || {};
    }

    vatBarWidth(amount) {
        const c = this.compliance;
        const max = Math.max(1, Math.abs(c.vat_output_month || 0), Math.abs(c.vat_input_month || 0));
        const pct = Math.round((Math.abs(amount || 0) / max) * 100);
        return `${Math.max(pct, 2)}%`;
    }

    // --- Drilldowns -------------------------------------------------------
    openMoves(domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "account.move",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: domain,
            target: "current",
        });
    }

    openAllInvoices() {
        this.openMoves(
            [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
            ],
            "Customer Invoices"
        );
    }

    openReceivables() {
        this.openMoves(
            [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
            ],
            "Outstanding Receivables"
        );
    }

    openPayables() {
        this.openMoves(
            [
                ["move_type", "=", "in_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
            ],
            "Outstanding Payables"
        );
    }

    openOverdue() {
        const today = new Date().toISOString().slice(0, 10);
        this.openMoves(
            [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
                ["invoice_date_due", "<", today],
            ],
            "Overdue Customer Payments"
        );
    }

    async openTaxReport() {
        const action = await this.orm.call("rn.saudi.dashboard", "action_open_tax_report", []);
        await this.action.doAction(action);
    }

    async openBankEntries() {
        const action = await this.orm.call("rn.saudi.dashboard", "action_open_bank_entries", []);
        await this.action.doAction(action);
    }

    async openProfitAndLoss() {
        const action = await this.orm.call("rn.saudi.dashboard", "action_open_profit_and_loss", []);
        await this.action.doAction(action);
    }

    openInvoice(invoiceId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move",
            res_id: invoiceId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    // --- Header actions ---------------------------------------------------
    createCustomerInvoice() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Create Invoice",
            res_model: "account.move",
            views: [[false, "form"]],
            target: "current",
            context: { default_move_type: "out_invoice" },
        });
    }

    createVendorBill() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Vendor Bill",
            res_model: "account.move",
            views: [[false, "form"]],
            target: "current",
            context: { default_move_type: "in_invoice" },
        });
    }

    async openReports() {
        const action = await this.orm.call("rn.saudi.dashboard", "action_open_reports", []);
        await this.action.doAction(action);
    }

    // --- Custom Arabic tooltip -------------------------------------------
    // Walks up from the hovered node to find a bilingual label group and
    // returns its English + Arabic text. Returns null when there is nothing
    // to translate, so plain text never triggers an empty tooltip.
    _findTipSource(target) {
        let el = target;
        while (el && el.classList && !el.classList.contains("o_rn_dashboard")) {
            const enEl = el.querySelector(":scope > .o_rn_lbl_en");
            const arEl = el.querySelector(":scope > .o_rn_lbl_ar");
            if (enEl && arEl) {
                const en = enEl.textContent.trim();
                const ar = arEl.textContent.trim();
                if (en && ar) {
                    return { el, en, ar };
                }
            }
            if (el.tagName === "TH") {
                const arTh = el.querySelector(".o_rn_th_ar");
                if (arTh) {
                    const ar = arTh.textContent.trim();
                    const en = el.textContent.replace(ar, "").trim();
                    if (en && ar) {
                        return { el, en, ar };
                    }
                }
            }
            el = el.parentElement;
        }
        return null;
    }

    onTipOver(ev) {
        const src = this._findTipSource(ev.target);
        if (!src) {
            return;
        }
        const rect = src.el.getBoundingClientRect();
        this.state.tip = {
            visible: true,
            en: src.en,
            ar: src.ar,
            x: Math.round(rect.left + rect.width / 2),
            y: Math.round(rect.top),
        };
    }

    onTipOut(ev) {
        const src = this._findTipSource(ev.target);
        if (!src) {
            return;
        }
        // Ignore moves that stay inside the same label group.
        if (ev.relatedTarget && src.el.contains(ev.relatedTarget)) {
            return;
        }
        this.state.tip.visible = false;
    }
}

registry.category("actions").add("rn_saudi_dashboard", SaudiDashboard);
