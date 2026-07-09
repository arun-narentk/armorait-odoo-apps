/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnTrusteeDashboard extends Component {
    static template = "rn_temple_core.TrusteeDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            donations: 0,
            donationCount: 0,
            festivals: 0,
            hundi: 0,
            devotees: 0,
        });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.temple.dashboard.service", "get_trustee_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            donations: data.donations_month || 0,
            donationCount: data.donation_count_month || 0,
            festivals: data.active_festivals || 0,
            hundi: data.hundi_pending || 0,
            devotees: data.devotee_count || 0,
        });
    }

    formatNumber(v) { return Number(v || 0).toLocaleString(); }
}

registry.category("actions").add("rn_temple_core.trustee_dashboard", RnTrusteeDashboard);
