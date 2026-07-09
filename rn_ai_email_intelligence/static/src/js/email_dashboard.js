/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnAiEmailDashboard extends Component {
    static template = "rn_ai_email_intelligence.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, cards: {}, updatedAt: "" });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.ai.email.dashboard.service", "get_dashboard_data", []);
        Object.assign(this.state, {
            loading: false,
            cards: data.cards || {},
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_ai_email_intelligence.dashboard", RnAiEmailDashboard);
