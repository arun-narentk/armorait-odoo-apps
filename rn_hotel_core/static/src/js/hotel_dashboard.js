/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnHotelDashboard extends Component {
    static template = "rn_hotel_core.HotelDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, occupancy: 0, arrivals: 0, departures: 0, revenue: 0, adr: 0, dirty: 0 });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.hotel.dashboard.service", "get_gm_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            occupancy: data.occupancy_pct || 0,
            arrivals: data.arrivals_today || 0,
            departures: data.departures_today || 0,
            revenue: data.revenue_today || 0,
            adr: data.adr || 0,
            dirty: data.dirty_rooms || 0,
        });
    }

    formatNumber(v) { return Number(v || 0).toLocaleString(); }
}

registry.category("actions").add("rn_hotel_core.hotel_dashboard", RnHotelDashboard);
