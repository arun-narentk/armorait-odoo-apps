/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnDoctorDashboard extends Component {
    static template = "rn_hospital_core.DoctorDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            doctorName: "",
            appointmentsToday: 0,
            inConsultation: 0,
            queue: [],
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
            "get_doctor_dashboard",
            []
        );
        Object.assign(this.state, {
            loading: false,
            doctorName: data.doctor_name || "",
            appointmentsToday: data.appointments_today || 0,
            inConsultation: data.in_consultation || 0,
            queue: data.queue || [],
            updatedAt: data.updated_at || "",
        });
    }
}

registry.category("actions").add("rn_hospital_core.doctor_dashboard", RnDoctorDashboard);
