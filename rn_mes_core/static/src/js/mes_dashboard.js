/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnMesDashboard extends Component {
    static template = "rn_mes_core.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            activeSessions: 0,
            pausedSessions: 0,
            openDowntime: 0,
            machines: {},
            oeeAvg: 0,
            goodQty: 0,
            scrapQty: 0,
            aiSummary: "",
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.mes.dashboard.service",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state, {
            loading: false,
            activeSessions: data.active_sessions || 0,
            pausedSessions: data.paused_sessions || 0,
            openDowntime: data.open_downtime || 0,
            machines: data.machines || {},
            oeeAvg: data.oee_avg || 0,
            goodQty: data.good_qty_today || 0,
            scrapQty: data.scrap_qty_today || 0,
            aiSummary: data.ai_summary || "",
            updatedAt: data.updated_at || "",
        });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }
}

registry.category("actions").add("rn_mes_core.dashboard", RnMesDashboard);
