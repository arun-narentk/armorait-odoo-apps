/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const STATUS_CLASS = {
    vacant: "bg-success",
    occupied: "bg-primary",
    dirty: "bg-warning",
    cleaning: "bg-info",
    maintenance: "bg-danger",
    reserved: "bg-secondary",
    blocked: "bg-dark",
};

export class RnHotelRoomBoard extends Component {
    static template = "rn_hotel_core.RoomBoard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: true, rooms: [] });
        onWillStart(async () => { await this.refresh(); });
    }

    statusClass(status) {
        return STATUS_CLASS[status] || "bg-light";
    }

    async refresh() {
        this.state.loading = true;
        this.state.rooms = await this.orm.call("rn.hotel.dashboard.service", "get_room_board", []);
        this.state.loading = false;
    }
}

registry.category("actions").add("rn_hotel_core.room_board", RnHotelRoomBoard);
