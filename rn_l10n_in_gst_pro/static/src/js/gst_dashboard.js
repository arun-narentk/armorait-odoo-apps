/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnGstDashboard extends Component {
    static template = "rn_l10n_in_gst_pro.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            returnCount: 0,
            pending: 0,
            validated: 0,
            mismatches: 0,
            outputGst: 0,
        });
        onWillStart(async () => {
            const kpis = await this.orm.call("rn.gst.dashboard.service", "get_kpis", []);
            this.state.returnCount = kpis.return_count || 0;
            this.state.pending = kpis.pending_returns || 0;
            this.state.validated = kpis.validated_returns || 0;
            this.state.mismatches = kpis.mismatch_count || 0;
            this.state.outputGst = kpis.output_gst || 0;
        });
    }
}

registry.category("actions").add("rn_l10n_in_gst_pro.dashboard", RnGstDashboard);
