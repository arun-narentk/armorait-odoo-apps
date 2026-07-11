/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";

const OFFICE_MIMETYPES = new Set([
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]);

export class RnPreviewDialog extends Component {
    static template = "rn_attachment_preview.PreviewDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        file: Object,
        mode: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            html: "",
            annotations: [],
            newNote: "",
            pageNumber: 1,
        });
        this.loadContent();
    }

    get title() {
        return this.props.file.name || _t("Preview");
    }

    get dialogProps() {
        return {
            title: this.title,
            size: "xl",
            contentClass: "rn_preview_dialog",
        };
    }

    get isOffice() {
        return this.props.mode === "office" || OFFICE_MIMETYPES.has(this.props.file.mimetype);
    }

    get isPdf() {
        return this.props.file.mimetype === "application/pdf" || this.props.mode === "pdf";
    }

    get pdfViewerUrl() {
        const contentUrl = url("/web/content/" + this.props.file.id, {
            filename: this.props.file.name,
        });
        return `/web/static/lib/pdfjs/web/viewer.html?file=${encodeURIComponent(contentUrl)}#pagemode=none`;
    }

    get officeHtml() {
        return markup(this.state.html || "<p><em>No preview available.</em></p>");
    }

    async loadContent() {
        try {
            if (this.isOffice) {
                const payload = await this.orm.call(
                    "rn.attachment.preview.service",
                    "get_office_preview",
                    [this.props.file.id]
                );
                this.state.html = payload.html || "";
            }
            if (this.isPdf) {
                this.state.annotations = await this.orm.call(
                    "rn.attachment.preview.service",
                    "get_pdf_annotations",
                    [this.props.file.id]
                );
            }
        } catch (error) {
            this.notification.add(error.message || _t("Preview failed."), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onAddAnnotation() {
        const note = (this.state.newNote || "").trim();
        if (!note) {
            this.notification.add(_t("Enter an annotation note."), { type: "warning" });
            return;
        }
        try {
            const created = await this.orm.call(
                "rn.attachment.preview.service",
                "create_pdf_annotation",
                [this.props.file.id],
                {
                    note,
                    page_number: this.state.pageNumber,
                }
            );
            this.state.annotations = [...this.state.annotations, created];
            this.state.newNote = "";
            this.notification.add(_t("Annotation saved."), { type: "success" });
        } catch (error) {
            this.notification.add(error.message || _t("Could not save annotation."), { type: "danger" });
        }
    }

    async onDeleteAnnotation(annotationId) {
        try {
            await this.orm.call(
                "rn.attachment.preview.service",
                "delete_pdf_annotation",
                [annotationId]
            );
            this.state.annotations = this.state.annotations.filter((row) => row.id !== annotationId);
        } catch (error) {
            this.notification.add(error.message || _t("Could not delete annotation."), { type: "danger" });
        }
    }
}
