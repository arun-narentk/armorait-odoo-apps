/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnRestaurantDashboard extends Component {
    static template = "rn_restaurant_core.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            cards: {},
            edition: "starter",
            suiteHint: "",
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString();
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.restaurant.dashboard.service", "get_dashboard_data", []);
        Object.assign(this.state, {
            loading: false,
            cards: data.cards || {},
            edition: data.edition || "starter",
            suiteHint: data.suite_hint || "",
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_restaurant_core.dashboard", RnRestaurantDashboard);
