/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Frontend service stub. Real data/realtime/AI services arrive later.
 */
export const rnKpiDashboardService = {
    dependencies: ["orm", "notification"],
    start(env, { orm, notification }) {
        return {
            async getDashboard(dashboardId) {
                if (!dashboardId) {
                    return null;
                }
                return orm.read("rn.kpi.dashboard", [dashboardId], [
                    "name",
                    "theme",
                    "layout_mode",
                    "auto_refresh",
                    "refresh_interval",
                ]);
            },
            notify(message, type = "info") {
                notification.add(message, { type });
            },
        };
    },
};

registry.category("services").add("rn_kpi_dashboard", rnKpiDashboardService);
