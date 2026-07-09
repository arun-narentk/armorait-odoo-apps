/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatNumber, formatPercent } from "./chart_utils";

export class RnDashboardShell extends Component {
    static template = "rn_dashboard_core.Shell";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            dashboard: {},
            cards: {},
            charts: {},
            alerts: [],
            widgets: [],
            statusLegend: [],
            updatedAt: "",
            edition: "basic",
            clock: "",
        });
        this._timer = null;
        this._clockTimer = null;
        onWillStart(async () => {
            await this.refresh();
        });
        onMounted(() => {
            this._clockTimer = setInterval(() => {
                this.state.clock = new Date().toLocaleString();
            }, 1000);
        });
        onWillUnmount(() => {
            if (this._timer) {
                clearInterval(this._timer);
            }
            if (this._clockTimer) {
                clearInterval(this._clockTimer);
            }
        });
    }

    get dashboardId() {
        return this.props.action?.params?.dashboard_id || false;
    }

    get filterId() {
        return this.props.action?.params?.filter_id || false;
    }

    formatNumber = formatNumber;
    formatPercent = formatPercent;

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.dashboard.service",
            "get_dashboard_data",
            [this.dashboardId, {}, this.filterId || false]
        );
        Object.assign(this.state, {
            loading: false,
            dashboard: data.dashboard || {},
            cards: data.cards || {},
            charts: data.charts || {},
            alerts: data.alerts || [],
            widgets: data.widgets || [],
            statusLegend: Object.entries(data.status_legend || {}).map(([key, color]) => ({ key, color })),
            updatedAt: data.updated_at || "",
            edition: data.edition || "basic",
            clock: new Date().toLocaleString(),
        });
        if (this._timer) {
            clearInterval(this._timer);
        }
        const seconds = Number(this.state.dashboard.refresh_interval || 0);
        if (seconds > 0) {
            this._timer = setInterval(() => this.refresh(), seconds * 1000);
        }
    }
}

registry.category("actions").add("rn_dashboard_core.shell", RnDashboardShell);
