/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnCrmDashboard extends Component {
    static template = "rn_crm_ultimate_pro.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            leads: 0,
            opportunities: 0,
            won: 0,
            lost: 0,
            revenue: 0,
            forecast: 0,
        });
        onWillStart(async () => {
            const kpis = await this.orm.call("rn.crm.dashboard.service", "get_kpis", []);
            Object.assign(this.state, {
                leads: kpis.leads || 0,
                opportunities: kpis.opportunities || 0,
                won: kpis.won || 0,
                lost: kpis.lost || 0,
                revenue: kpis.revenue || 0,
                forecast: kpis.forecast || 0,
            });
        });
    }
}

registry.category("actions").add("rn_crm_ultimate_pro.dashboard", RnCrmDashboard);
