/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class TempleDashboard extends Component {
    static template = "rn_temple_base.TempleDashboard";

    setup() {
        this.state = useState({ cards: [], festivals: [] });
        onWillStart(async () => {
            const data = await rpc("/rn_temple_base/dashboard/data");
            const cards = data.cards || {};
            this.state.cards = [
                { key: "temples", label: "Temples", value: cards.temples || 0 },
                { key: "branches", label: "Branches", value: cards.branches || 0 },
                { key: "trustees", label: "Trustees", value: cards.trustees || 0 },
                { key: "priests", label: "Priests", value: cards.priests || 0 },
                { key: "festivals", label: "Upcoming Festivals", value: cards.upcoming_festivals || 0 },
                { key: "departments", label: "Departments", value: cards.departments || 0 },
            ];
            this.state.festivals = data.festivals || [];
        });
    }
}

registry.category("actions").add("rn_temple_dashboard", TempleDashboard);
