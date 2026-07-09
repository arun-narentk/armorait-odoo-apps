/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnErpHealthDashboard extends Component {
    static template = "rn_erp_health_analyzer.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            data: {},
        });
        onWillStart(async () => {
            await this.reload();
        });
    }

    async reload() {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "rn.erp.health.dashboard.service",
            "get_dashboard_data",
            []
        );
        this.state.loading = false;
    }
}

registry.category("actions").add("rn_erp_health_analyzer.dashboard", RnErpHealthDashboard);
