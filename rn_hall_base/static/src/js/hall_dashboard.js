/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class HallDashboard extends Component {
    static template = "rn_hall_base.HallDashboard";

    setup() {
        this.state = useState({ cards: [], bookings: [] });
        onWillStart(async () => {
            const data = await rpc("/rn_hall_base/dashboard/data");
            const cards = data.cards || {};
            this.state.cards = [
                { key: "venues", label: "Venues", value: cards.venues || 0 },
                { key: "halls", label: "Halls", value: cards.halls || 0 },
                { key: "upcoming", label: "Upcoming", value: cards.upcoming_bookings || 0 },
                { key: "confirmed", label: "Confirmed", value: cards.confirmed_bookings || 0 },
                { key: "tentative", label: "Tentative", value: cards.tentative_bookings || 0 },
                { key: "occupancy", label: "Occupancy %", value: cards.occupancy_rate || 0 },
            ];
            this.state.bookings = data.bookings || [];
        });
    }
}

registry.category("actions").add("rn_hall_dashboard", HallDashboard);
