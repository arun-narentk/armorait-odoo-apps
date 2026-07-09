/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnSchoolDashboard extends Component {
    static template = "rn_school_core.SchoolDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, enrolled: 0, enquiries: 0, feesDue: 0, sessionsToday: 0 });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.school.dashboard.service", "get_principal_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            enrolled: data.enrolled_students || 0,
            enquiries: data.new_enquiries || 0,
            feesDue: data.fees_outstanding || 0,
            sessionsToday: data.attendance_sessions_today || 0,
        });
    }

    formatNumber(v) { return Number(v || 0).toLocaleString(); }
}

registry.category("actions").add("rn_school_core.school_dashboard", RnSchoolDashboard);
