/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnVetDashboard extends Component {
    static template = "rn_veterinary_core.VetDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            appointments: 0,
            surgeries: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.vet.dashboard.service", "get_vet_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            appointments: data.appointments_today || 0,
            surgeries: data.surgeries_pending || 0,
        });
    }
}

registry.category("actions").add("rn_veterinary_core.vet_dashboard", RnVetDashboard);
