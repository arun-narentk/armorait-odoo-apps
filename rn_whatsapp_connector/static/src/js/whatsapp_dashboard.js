/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnWhatsappDashboard extends Component {
    static template = "rn_whatsapp_connector.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            today: 0,
            delivered: 0,
            failed: 0,
            pending: 0,
        });
        onWillStart(async () => {
            await this.loadStats();
        });
    }

    async loadStats() {
        this.state.today = await this.orm.searchCount("rn.whatsapp.message", []);
        this.state.delivered = await this.orm.searchCount("rn.whatsapp.message", [["status", "=", "delivered"]]);
        this.state.failed = await this.orm.searchCount("rn.whatsapp.message", [["status", "=", "failed"]]);
        this.state.pending = await this.orm.searchCount("rn.whatsapp.message", [["status", "in", ["draft", "queued"]]]);
    }
}

registry.category("actions").add("rn_whatsapp_connector.dashboard", RnWhatsappDashboard);
