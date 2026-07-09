/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnWorkflowDashboard extends Component {
    static template = "rn_workflow_builder.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            totalWorkflows: 0,
            activeWorkflows: 0,
            runs7d: 0,
            failedRuns: 0,
            retryQueue: 0,
            successRate: 0,
            avgDurationMs: 0,
            suggestions: [],
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.workflow.monitor.service",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state, {
            loading: false,
            totalWorkflows: data.total_workflows || 0,
            activeWorkflows: data.active_workflows || 0,
            runs7d: data.runs_7d || 0,
            failedRuns: data.failed_runs || 0,
            retryQueue: data.retry_queue || 0,
            successRate: data.success_rate || 0,
            avgDurationMs: data.avg_duration_ms || 0,
            suggestions: data.suggestions || [],
            updatedAt: data.updated_at || "",
        });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }
}

registry.category("actions").add("rn_workflow_builder.dashboard", RnWorkflowDashboard);
