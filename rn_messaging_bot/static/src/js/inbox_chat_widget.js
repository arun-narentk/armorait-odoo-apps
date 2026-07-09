/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, useEffect } from "@odoo/owl";

export class RnMessagingInboxChatWidget extends Component {
    static template = "rn_messaging_bot.InboxChat";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            conversation: {},
            messages: [],
            templates: [],
            draft: "",
            templateId: false,
            sending: false,
        });
        onWillStart(async () => {
            await this.reload();
        });
        useEffect(
            () => {
                const conversationId = this.props.record.resId;
                if (conversationId) {
                    this.reload();
                }
            },
            () => [this.props.record.resId]
        );
    }

    get conversationId() {
        return this.props.record.resId;
    }

    async reload() {
        if (!this.conversationId) {
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.messaging.conversation",
            "get_inbox_chat_data",
            [this.conversationId]
        );
        this.state.conversation = data.conversation || {};
        this.state.messages = data.messages || [];
        this.state.templates = data.templates || [];
        this.state.loading = false;
    }

    messageClass(message) {
        return message.direction === "outbound"
            ? "o_rn_chat_bubble o_rn_chat_outbound"
            : "o_rn_chat_bubble o_rn_chat_inbound";
    }

    async sendMessage() {
        if (!this.state.draft.trim() || this.state.sending) {
            return;
        }
        this.state.sending = true;
        try {
            const data = await this.orm.call(
                "rn.messaging.conversation",
                "post_agent_reply",
                [this.conversationId],
                {
                    body: this.state.draft,
                    template_id: this.state.templateId || false,
                }
            );
            this.state.conversation = data.conversation || this.state.conversation;
            this.state.messages = data.messages || [];
            this.state.draft = "";
            this.state.templateId = false;
            this.notification.add("Message sent.", { type: "success" });
        } finally {
            this.state.sending = false;
        }
    }

    onTemplateChange(ev) {
        const value = parseInt(ev.target.value, 10);
        this.state.templateId = value || false;
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }
}

export const rnMessagingInboxChat = {
    component: RnMessagingInboxChatWidget,
};

registry.category("view_widgets").add("rn_messaging_inbox_chat", rnMessagingInboxChat);
