/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, useEffect } from "@odoo/owl";

const ICON_LABELS = {
    warning: "Warning",
    vip: "VIP",
    finance: "Finance",
    logistics: "Logistics",
    call: "Call",
    technical: "Technical",
    general: "General",
    urgent: "Urgent",
};

export class RnSmartNotesPanelWidget extends Component {
    static template = "rn_smart_notes.SmartNotesPanel";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            notes: [],
            templates: [],
            quickTemplates: [],
            showComposer: false,
            draftName: "",
            draftNote: "",
            draftColor: "yellow",
            draftPriority: "medium",
            draftIcon: "general",
            draftPinned: false,
            editingId: null,
        });
        onWillStart(async () => {
            await this.reload();
        });
        useEffect(
            () => {
                if (this.props.record.resId) {
                    this.reload();
                }
            },
            () => [this.props.record.resId]
        );
    }

    get resModel() {
        return this.props.record.resModel;
    }

    get resId() {
        return this.props.record.resId;
    }

    iconLabel(icon) {
        return ICON_LABELS[icon] || "General";
    }

    async reload() {
        if (!this.resId) {
            this.state.loading = false;
            this.state.notes = [];
            return;
        }
        this.state.loading = true;
        const data = await this.orm.call("rn.smart.note", "get_panel_data", [
            this.resModel,
            this.resId,
        ]);
        this.state.notes = data.notes || [];
        this.state.templates = data.templates || [];
        this.state.quickTemplates = data.quick_templates || [];
        this.state.loading = false;
    }

    resetComposer() {
        this.state.showComposer = false;
        this.state.editingId = null;
        this.state.draftName = "";
        this.state.draftNote = "";
        this.state.draftColor = "yellow";
        this.state.draftPriority = "medium";
        this.state.draftIcon = "general";
        this.state.draftPinned = false;
    }

    openComposer() {
        this.resetComposer();
        this.state.showComposer = true;
    }

    editNote(note) {
        this.state.editingId = note.id;
        this.state.draftName = note.name;
        this.state.draftNote = note.note;
        this.state.draftColor = note.color;
        this.state.draftPriority = note.priority;
        this.state.draftIcon = note.icon;
        this.state.draftPinned = note.is_pinned;
        this.state.showComposer = true;
    }

    async saveNote() {
        if (!this.state.draftName.trim()) {
            this.notification.add("Title is required.", { type: "warning" });
            return;
        }
        const payload = {
            name: this.state.draftName.trim(),
            note: this.state.draftNote,
            color: this.state.draftColor,
            priority: this.state.draftPriority,
            icon: this.state.draftIcon,
            is_pinned: this.state.draftPinned,
            visibility: "everyone",
        };
        if (this.state.editingId) {
            await this.orm.call("rn.smart.note", "update_from_panel", [
                this.state.editingId,
                payload,
            ]);
            this.notification.add("Note updated.", { type: "success" });
        } else {
            await this.orm.call("rn.smart.note", "create_from_panel", [
                this.resModel,
                this.resId,
                payload,
            ]);
            this.notification.add("Note added.", { type: "success" });
        }
        this.resetComposer();
        await this.reload();
        await this.props.record.load();
    }

    async quickAdd(templateId) {
        await this.orm.call("rn.smart.note", "create_from_panel", [
            this.resModel,
            this.resId,
            { template_id: templateId },
        ]);
        this.notification.add("Quick note added.", { type: "success" });
        await this.reload();
        await this.props.record.load();
    }

    async togglePin(note) {
        await this.orm.call("rn.smart.note", "update_from_panel", [note.id, {
            is_pinned: !note.is_pinned,
        }]);
        await this.reload();
        await this.props.record.load();
    }

    async deleteNote(note) {
        await this.orm.call("rn.smart.note", "delete_from_panel", [note.id]);
        this.notification.add("Note deleted.", { type: "success" });
        await this.reload();
        await this.props.record.load();
    }
}

export const rnSmartNotesPanel = {
    component: RnSmartNotesPanelWidget,
};

registry.category("view_widgets").add("rn_smart_notes_panel", rnSmartNotesPanel);
