/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatMoney, normalizeChart } from "./chart_utils";

export class RnBiSalesDashboard extends Component {
    static template = "rn_bi_sales_dashboard.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            datePreset: "this_month",
            cards: {},
            charts: {},
            tops: {},
            forecast: {},
            filters: {},
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    getFormatted(value) {
        return formatMoney(value);
    }

    monthlyTrend() {
        return normalizeChart(this.state.charts.monthly_trend);
    }

    async refresh() {
        this.state.loading = true;
        const ctx = this.props.action?.context || {};
        const biFilters = ctx.bi_filters || { date_preset: this.state.datePreset };
        const data = await this.orm.call("rn.bi.dashboard.service", "get_dashboard_data", [biFilters]);
        Object.assign(this.state, {
            loading: false,
            cards: data.cards || {},
            charts: data.charts || {},
            tops: data.tops || {},
            forecast: data.forecast || {},
            filters: data.filters || {},
            datePreset: (data.filters && data.filters.date_preset) || this.state.datePreset,
        });
    }

    async onPresetChange(ev) {
        this.state.datePreset = ev.target.value;
        const data = await this.orm.call("rn.bi.dashboard.service", "get_dashboard_data", [{
            date_preset: this.state.datePreset,
        }]);
        Object.assign(this.state, {
            cards: data.cards || {},
            charts: data.charts || {},
            tops: data.tops || {},
            forecast: data.forecast || {},
            filters: data.filters || {},
        });
    }
}

registry.category("actions").add("rn_bi_sales_dashboard.dashboard", RnBiSalesDashboard);
