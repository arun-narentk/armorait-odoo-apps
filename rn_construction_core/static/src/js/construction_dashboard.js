/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnConstructionDashboard extends Component {
    static template = "rn_construction_core.ConstructionDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            active: 0,
            delayed: 0,
            budget: 0,
            actual: 0,
            variance: 0,
            issues: 0,
            pendingMr: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.construction.dashboard.service",
            "get_management_dashboard",
            []
        );
        Object.assign(this.state, {
            loading: false,
            active: data.active_projects || 0,
            delayed: data.delayed_projects || 0,
            budget: data.budget_total || 0,
            actual: data.actual_cost || 0,
            variance: data.variance || 0,
            issues: data.open_issues || 0,
            pendingMr: data.pending_mr || 0,
        });
    }

    formatNumber(v) { return Number(v || 0).toLocaleString(); }
}

registry.category("actions").add("rn_construction_core.construction_dashboard", RnConstructionDashboard);
