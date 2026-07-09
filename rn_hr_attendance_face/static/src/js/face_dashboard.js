/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnFaceDashboard extends Component {
    static template = "rn_hr_attendance_face.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            present: 0,
            unknown: 0,
            spoof: 0,
            lowConfidence: 0,
        });
        onWillStart(async () => {
            await this.loadStats();
        });
    }

    async loadStats() {
        this.state.present = await this.orm.searchCount("rn.hr.attendance.log", [
            ["recognition_result", "in", ["check_in", "check_out"]],
        ]);
        this.state.unknown = await this.orm.searchCount("rn.hr.attendance.log", [
            ["recognition_result", "=", "unknown_face"],
        ]);
        this.state.spoof = await this.orm.searchCount("rn.hr.attendance.log", [
            ["recognition_result", "=", "spoof"],
        ]);
        this.state.lowConfidence = await this.orm.searchCount("rn.hr.attendance.log", [
            ["recognition_result", "=", "low_confidence"],
        ]);
    }
}

registry.category("actions").add("rn_hr_attendance_face.dashboard", RnFaceDashboard);
