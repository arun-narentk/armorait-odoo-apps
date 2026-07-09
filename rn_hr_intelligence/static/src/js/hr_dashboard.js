/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, markup } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnHrDashboard extends Component {
    static template = "rn_hr_intelligence.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            executive: {},
            overtime: {},
            attrition: {},
            departments: [],
            qualityIssues: 0,
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

    formatMoney(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.hr.dashboard.service", "get_dashboard_data", []);
        Object.assign(this.state, {
            loading: false,
            executive: data.executive || {},
            overtime: data.overtime || {},
            attrition: data.attrition || {},
            departments: data.departments || [],
            qualityIssues: data.quality_issues || 0,
            aiSummary: data.ai_summary || "",
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_hr_intelligence.dashboard", RnHrDashboard);
