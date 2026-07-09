/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class RealestateDashboard extends Component {
    static template = "rn_realestate_base.RealestateDashboard";

    setup() {
        this.state = useState({ cards: [], pipeline: [] });
        onWillStart(async () => {
            const data = await rpc("/rn_realestate_base/dashboard/data");
            const cards = data.cards || {};
            this.state.cards = [
                { key: "projects", label: "Projects", value: cards.projects || 0 },
                { key: "available", label: "Available Units", value: cards.available_units || 0 },
                { key: "booked", label: "Booked", value: cards.booked_units || 0 },
                { key: "sold", label: "Sold", value: cards.sold_units || 0 },
                { key: "leads", label: "Active Leads", value: cards.active_leads || 0 },
                { key: "sell_through", label: "Sell-through %", value: cards.sell_through || 0 },
            ];
            this.state.pipeline = data.pipeline || [];
        });
    }
}

registry.category("actions").add("rn_realestate_dashboard", RealestateDashboard);
