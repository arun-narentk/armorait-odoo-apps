/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { markup } from "@odoo/owl";

export class RnMrpDashboard extends Component {
    static template = "rn_mrp_intelligence.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            executive: {},
            production: {},
            inventory: {},
            workcenters: {},
            oeeAvg: 0,
            aiSummary: "",
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    get aiSummaryMarkup() {
        return this.state.aiSummary ? markup(this.state.aiSummary) : "";
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.mrp.dashboard.service",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state, {
            loading: false,
            executive: data.executive || {},
            production: data.production || {},
            inventory: data.inventory || {},
            workcenters: data.workcenters || {},
            oeeAvg: data.oee_avg || 0,
            aiSummary: data.ai_summary || "",
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_mrp_intelligence.dashboard", RnMrpDashboard);
