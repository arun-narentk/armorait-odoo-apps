/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnMesTablet extends Component {
    static template = "rn_mes_core.Tablet";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            terminalId: false,
            session: {},
            workorder: {},
            pending: [],
            barcode: "",
            message: "",
        });
        onWillStart(async () => {
            const params = this.props.action?.params || {};
            await this.load(params.terminal_id, params.workorder_id);
        });
    }

    async load(terminalId, workorderId) {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.mes.execution.service",
            "get_tablet_payload",
            [],
            { terminal_id: terminalId, workorder_id: workorderId }
        );
        this.state.terminalId = data.terminal?.id || false;
        this.state.session = data.session || {};
        this.state.workorder = data.workorder || {};
        this.state.pending = data.pending_workorders || [];
        this.state.loading = false;
    }

    async onScan() {
        if (!this.state.barcode) {
            return;
        }
        const result = await this.orm.call(
            "rn.mes.barcode.service",
            "process_scan",
            [this.state.barcode],
            { terminal_id: this.state.terminalId, session_id: this.state.session.id }
        );
        this.state.message = `Scanned: ${result.scan_type} (${result.res_id || "n/a"})`;
        this.state.barcode = "";
    }

    formatQty(value) {
        return Number(value || 0).toLocaleString();
    }
}

registry.category("actions").add("rn_mes_core.tablet", RnMesTablet);
