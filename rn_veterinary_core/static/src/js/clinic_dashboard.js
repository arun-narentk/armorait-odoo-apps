/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnVetClinicDashboard extends Component {
    static template = "rn_veterinary_core.ClinicDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            appointments: 0,
            vaccinesDue: 0,
            boarding: 0,
            grooming: 0,
            pets: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.vet.dashboard.service", "get_clinic_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            appointments: data.appointments_today || 0,
            vaccinesDue: data.vaccinations_due || 0,
            boarding: data.boarding_occupancy || 0,
            grooming: data.grooming_month || 0,
            pets: data.pet_count || 0,
        });
    }
}

registry.category("actions").add("rn_veterinary_core.clinic_dashboard", RnVetClinicDashboard);
