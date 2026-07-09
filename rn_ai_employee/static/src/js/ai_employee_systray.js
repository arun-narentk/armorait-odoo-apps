/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService } from "@web/core/utils/hooks";

export class AiEmployeeSystray extends Component {
    static template = "rn_ai_employee.Systray";
    static components = { Dropdown };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.messagesRef = useRef("messages");
        this.state = useState({
            open: false,
            loading: true,
            sending: false,
            chatId: null,
            messages: [],
            suggestions: [],
            draft: "",
            error: "",
        });
        onWillStart(async () => {
            await this.bootstrap();
        });
        onMounted(() => {
            this._scrollToBottom();
        });
    }

    async bootstrap() {
        this.state.loading = true;
        this.state.error = "";
        try {
            const data = await this.orm.call("rn.ai.employee.chat", "widget_bootstrap", []);
            this.state.chatId = data.chat_id;
            this.state.messages = data.messages || [];
            this.state.suggestions = data.suggestions || [];
        } catch (error) {
            this.state.error = error.message || "AI Copilot is unavailable.";
        } finally {
            this.state.loading = false;
            this._scrollToBottom();
        }
    }

    async sendMessage(question) {
        const message = (question || this.state.draft || "").trim();
        if (!message || !this.state.chatId || this.state.sending) {
            return;
        }
        this.state.sending = true;
        this.state.error = "";
        this.state.draft = "";
        try {
            const data = await this.orm.call(
                "rn.ai.employee.chat",
                "widget_send_message",
                [this.state.chatId, message]
            );
            this.state.messages = data.messages || [];
        } catch (error) {
            this.state.error = error.message || "Could not send the message.";
        } finally {
            this.state.sending = false;
            this._scrollToBottom();
        }
    }

    async onRunAction(actionId) {
        const clientAction = await this.orm.call(
            "rn.ai.employee.chat",
            "widget_run_action",
            [actionId]
        );
        if (clientAction && clientAction.messages) {
            this.state.messages = clientAction.messages;
            this._scrollToBottom();
            return;
        }
        if (clientAction) {
            this.action.doAction(clientAction);
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    _scrollToBottom() {
        const node = this.messagesRef.el;
        if (node) {
            node.scrollTop = node.scrollHeight;
        }
    }
}

registry.category("systray").add(
    "rn_ai_employee.Systray",
    { Component: AiEmployeeSystray },
    { sequence: 90 }
);
