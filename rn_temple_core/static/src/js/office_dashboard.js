/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnOfficeDashboard extends Component {
    static template = "rn_temple_core.OfficeDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            bookings: 0,
            receipts: 0,
            festivals: 0,
            annadhanam: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.temple.dashboard.service", "get_office_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            bookings: data.bookings_today || 0,
            receipts: data.pending_receipts || 0,
            festivals: data.upcoming_festivals || 0,
            annadhanam: data.annadhanam_today || 0,
        });
    }
}

registry.category("actions").add("rn_temple_core.office_dashboard", RnOfficeDashboard);
