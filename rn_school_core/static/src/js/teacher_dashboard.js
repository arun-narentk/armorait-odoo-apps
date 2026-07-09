/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnTeacherDashboard extends Component {
    static template = "rn_school_core.TeacherDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, teacherName: "", classes: [], homeworkPending: 0 });
        onWillStart(async () => { await this.refresh(); });
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.school.dashboard.service", "get_teacher_dashboard", []);
        Object.assign(this.state, {
            loading: false,
            teacherName: data.teacher_name || "",
            classes: data.classes_today || [],
            homeworkPending: data.homework_to_grade || 0,
        });
    }
}

registry.category("actions").add("rn_school_core.teacher_dashboard", RnTeacherDashboard);
