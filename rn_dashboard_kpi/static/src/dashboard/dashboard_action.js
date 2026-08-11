/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

/**
 * Phase 1 client action stub.
 * Full shell, grid, and item renderers arrive in the OWL UI phase.
 */
export class RnKpiDashboardAction extends Component {
    static template = "rn_dashboard_kpi.DashboardAction";
    static props = { ...standardActionServiceProps };

    get dashboardId() {
        return this.props.action?.params?.dashboard_id || false;
    }

    get title() {
        return this.props.action?.name || "Dashboard KPI Studio";
    }
}

registry.category("actions").add("rn_dashboard_kpi.dashboard", RnKpiDashboardAction);
