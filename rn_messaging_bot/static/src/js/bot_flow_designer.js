/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnMessagingFlowDesigner extends Component {
    static template = "rn_messaging_bot.FlowDesigner";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.canvasRef = useRef("canvas");
        this.state = useState({
            loading: true,
            bot: {},
            nodes: [],
            edges: [],
            dragNodeId: null,
            dragOffsetX: 0,
            dragOffsetY: 0,
        });
        this._onMouseMove = this.onMouseMove.bind(this);
        this._onMouseUp = this.onMouseUp.bind(this);
        onWillStart(async () => {
            const botId = this.props.action?.params?.bot_id;
            if (botId) {
                await this.load(botId);
            } else {
                this.state.loading = false;
            }
        });
    }

    async load(botId) {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.messaging.bot",
            "get_designer_data",
            [botId]
        );
        this.state.bot = data.bot || {};
        this.state.nodes = data.nodes || [];
        this.state.edges = data.edges || [];
        this.state.loading = false;
    }

    nodeStyle(node) {
        return `left:${node.pos_x}px;top:${node.pos_y}px;`;
    }

    edgePath(edge) {
        const source = this.state.nodes.find((node) => node.id === edge.source);
        const target = this.state.nodes.find((node) => node.id === edge.target);
        if (!source || !target) {
            return "";
        }
        const x1 = source.pos_x + 90;
        const y1 = source.pos_y + 36;
        const x2 = target.pos_x + 90;
        const y2 = target.pos_y;
        return `M ${x1} ${y1} C ${x1} ${y1 + 40}, ${x2} ${y2 - 40}, ${x2} ${y2}`;
    }

    onNodeMouseDown(ev, node) {
        this.state.dragNodeId = node.id;
        const rect = this.canvasRef.el.getBoundingClientRect();
        this.state.dragOffsetX = ev.clientX - rect.left - node.pos_x;
        this.state.dragOffsetY = ev.clientY - rect.top - node.pos_y;
        document.addEventListener("mousemove", this._onMouseMove);
        document.addEventListener("mouseup", this._onMouseUp);
    }

    onMouseMove(ev) {
        if (!this.state.dragNodeId) {
            return;
        }
        const rect = this.canvasRef.el.getBoundingClientRect();
        const node = this.state.nodes.find((item) => item.id === this.state.dragNodeId);
        if (!node) {
            return;
        }
        node.pos_x = Math.max(0, ev.clientX - rect.left - this.state.dragOffsetX);
        node.pos_y = Math.max(0, ev.clientY - rect.top - this.state.dragOffsetY);
    }

    onMouseUp() {
        this.state.dragNodeId = null;
        document.removeEventListener("mousemove", this._onMouseMove);
        document.removeEventListener("mouseup", this._onMouseUp);
    }

    async saveLayout() {
        if (!this.state.bot.id) {
            return;
        }
        const layout = this.state.nodes.map((node) => ({
            id: node.id,
            pos_x: node.pos_x,
            pos_y: node.pos_y,
        }));
        await this.orm.call(
            "rn.messaging.bot",
            "save_designer_layout",
            [this.state.bot.id, layout]
        );
        this.notification.add("Flow layout saved.", { type: "success" });
    }
}

registry.category("actions").add("rn_messaging_bot.flow_designer", RnMessagingFlowDesigner);
