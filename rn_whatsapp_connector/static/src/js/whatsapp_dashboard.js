/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnWhatsappDashboard extends Component {
    static template = "rn_whatsapp_connector.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            cards: {},
            edition: "professional",
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.whatsapp.dashboard.service", "get_dashboard_data", []);
        Object.assign(this.state, {
            loading: false,
            cards: data.cards || {},
            edition: data.edition || "professional",
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_whatsapp_connector.dashboard", RnWhatsappDashboard);
