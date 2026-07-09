/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillUnmount } from "@odoo/owl";

/**
 * Full-screen kiosk shell. Webcam + live recognition arrive in Phase 4.
 */
export class RnFaceKiosk extends Component {
    static template = "rn_hr_attendance_face.Kiosk";

    setup() {
        this.state = useState({
            clock: new Date().toLocaleTimeString(),
            status: "Ready",
            message: "Phase 1 kiosk shell. Webcam recognition arrives in Phase 4.",
        });
        this._timer = setInterval(() => {
            this.state.clock = new Date().toLocaleTimeString();
        }, 1000);
        onWillUnmount(() => clearInterval(this._timer));
    }
}

registry.category("actions").add("rn_hr_attendance_face.kiosk", RnFaceKiosk);
