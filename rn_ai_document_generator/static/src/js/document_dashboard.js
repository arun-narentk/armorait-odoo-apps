/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnAiDocumentDashboard extends Component {
    static template = "rn_ai_document_generator.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, cards: {}, edition: "marketplace", updatedAt: "" });
        onWillStart(async () => { await this.refresh(); });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString();
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.ai.document.dashboard.service", "get_dashboard_data", []);
        Object.assign(this.state, {
            loading: false,
            cards: data.cards || {},
            edition: data.edition || "marketplace",
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_ai_document_generator.dashboard", RnAiDocumentDashboard);
