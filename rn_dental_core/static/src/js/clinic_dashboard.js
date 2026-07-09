/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnClinicDashboard extends Component {
    static template = "rn_dental_core.ClinicDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            appointments: 0,
            inChair: 0,
            utilization: 0,
            newPatients: 0,
            recalls: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.dental.dashboard.service", "get_clinic_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            appointments: data.appointments_today || 0,
            inChair: data.in_chair || 0,
            utilization: data.chair_utilization || 0,
            newPatients: data.new_patients_month || 0,
            recalls: data.pending_recalls || 0,
        });
    }
}

registry.category("actions").add("rn_dental_core.clinic_dashboard", RnClinicDashboard);
