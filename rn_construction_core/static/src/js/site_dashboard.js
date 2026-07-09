/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnSiteDashboard extends Component {
    static template = "rn_construction_core.SiteDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            sites: 0,
            issues: 0,
            pendingMr: 0,
            logsToday: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.construction.dashboard.service",
            "get_site_engineer_dashboard",
            []
        );
        Object.assign(this.state, {
            loading: false,
            sites: data.site_count || 0,
            issues: data.open_issues || 0,
            pendingMr: data.pending_mr || 0,
            logsToday: data.logs_today || 0,
        });
    }
}

registry.category("actions").add("rn_construction_core.site_dashboard", RnSiteDashboard);
