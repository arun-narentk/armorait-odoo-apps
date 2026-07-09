/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnHospitalDashboard extends Component {
    static template = "rn_hospital_core.HospitalDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            opdToday: 0,
            ipAdmissions: 0,
            bedOccupancy: 0,
            revenueToday: 0,
            waitingPatients: 0,
            updatedAt: "",
        });
        onWillStart(async () => {
            await this.refresh();
        });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.hospital.dashboard.service",
            "get_hospital_dashboard",
            []
        );
        Object.assign(this.state, {
            loading: false,
            opdToday: data.opd_today || 0,
            ipAdmissions: data.ip_admissions || 0,
            bedOccupancy: data.bed_occupancy_pct || 0,
            revenueToday: data.revenue_today || 0,
            waitingPatients: data.waiting_patients || 0,
            updatedAt: data.updated_at || "",
        });
    }

    formatNumber(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 });
    }
}

registry.category("actions").add("rn_hospital_core.hospital_dashboard", RnHospitalDashboard);
