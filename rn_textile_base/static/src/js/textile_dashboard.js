/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class TextileDashboard extends Component {
    static template = "rn_textile_base.TextileDashboard";

    setup() {
        this.state = useState({ cards: [], machineStates: [] });
        onWillStart(async () => {
            const data = await rpc("/rn_textile_base/dashboard/data");
            const cards = data.cards || {};
            this.state.cards = [
                { key: "factories", label: "Factories", value: cards.factories || 0 },
                { key: "departments", label: "Departments", value: cards.departments || 0 },
                { key: "machines", label: "Machines", value: cards.machines || 0 },
                { key: "active", label: "Active Machines", value: cards.active_machines || 0 },
                { key: "utilization", label: "Utilization %", value: cards.utilization_rate || 0 },
                { key: "yarn_specs", label: "Yarn Specs", value: cards.yarn_specs || 0 },
            ];
            this.state.machineStates = data.machines_by_state || [];
        });
    }
}

registry.category("actions").add("rn_textile_dashboard", TextileDashboard);
