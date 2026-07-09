/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnDentistDashboard extends Component {
    static template = "rn_dental_core.DentistDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            appointments: 0,
            treatments: 0,
            labPending: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.dental.dashboard.service", "get_dentist_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            appointments: data.appointments_today || 0,
            treatments: data.pending_treatments || 0,
            labPending: data.lab_pending || 0,
        });
    }
}

registry.category("actions").add("rn_dental_core.dentist_dashboard", RnDentistDashboard);
