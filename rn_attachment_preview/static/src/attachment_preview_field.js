/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { useService } from "@web/core/utils/hooks";
import { url } from "@web/core/utils/urls";
import { Many2ManyBinaryField, many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field";
import { registry } from "@web/core/registry";
import { RnPreviewDialog } from "./preview_dialog";

const TEXT_MIMETYPES = new Set([
    "text/plain",
    "text/csv",
    "text/xml",
    "application/xml",
    "application/json",
    "text/html",
    "application/javascript",
]);

const IMAGE_MIMETYPES = new Set([
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/svg+xml",
    "image/webp",
    "image/x-icon",
]);

const VIDEO_MIMETYPES = new Set([
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/webm",
]);

const OFFICE_MIMETYPES = new Set([
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]);

function toPreviewFile(file) {
    const mimetype = file.mimetype || "";
    const id = file.id;
    const name = file.name || "";
    const model = {
        id,
        name,
        mimetype,
        type: "binary",
        checksum: file.checksum,
        get isImage() {
            return IMAGE_MIMETYPES.has(mimetype);
        },
        get isPdf() {
            return mimetype.startsWith("application/pdf");
        },
        get isOffice() {
            return OFFICE_MIMETYPES.has(mimetype);
        },
        get isVideo() {
            return VIDEO_MIMETYPES.has(mimetype);
        },
        get isText() {
            return TEXT_MIMETYPES.has(mimetype);
        },
        get isViewable() {
            return (this.isText || this.isImage || this.isVideo || this.isPdf || this.isOffice) && !this.uploading;
        },
        get urlRoute() {
            return this.isImage ? `/web/image/${id}` : `/web/content/${id}`;
        },
        get urlQueryParams() {
            return { filename: name };
        },
        get defaultSource() {
            const route = url(this.urlRoute, this.urlQueryParams);
            if (this.isPdf) {
                return `/web/static/lib/pdfjs/web/viewer.html?file=${encodeURIComponent(route)}#pagemode=none`;
            }
            return route;
        },
        get downloadUrl() {
            return url(this.urlRoute, { ...this.urlQueryParams, download: true });
        },
        uploading: false,
    };
    return model;
}

export class RnAttachmentPreviewField extends Many2ManyBinaryField {
    static template = "rn_attachment_preview.AttachmentPreviewField";

    setup() {
        super.setup();
        this.fileViewer = useFileViewer();
        this.dialog = useService("dialog");
        this.hoverFileId = null;
    }

    toPreviewFiles() {
        return this.files.map((file) => toPreviewFile(file));
    }

    isPreviewable(file) {
        return toPreviewFile(file).isViewable;
    }

    getThumbnailUrl(file) {
        return `/web/image/ir.attachment/${file.id}/rn_preview_thumbnail`;
    }

    onThumbnailError(ev) {
        const target = ev.target;
        target.classList.add("o_image");
        target.removeAttribute("src");
        if (target.dataset.fallbackMimetype) {
            target.dataset.mimetype = target.dataset.fallbackMimetype;
        }
        if (target.dataset.fallbackExt) {
            target.dataset.ext = target.dataset.fallbackExt;
        }
    }

    onPreviewClick(file, ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const previewFile = toPreviewFile(file);
        if (!previewFile.isViewable) {
            return;
        }
        if (previewFile.isOffice) {
            this.dialog.add(RnPreviewDialog, { file: previewFile, mode: "office" });
            return;
        }
        if (previewFile.isPdf) {
            this.dialog.add(RnPreviewDialog, { file: previewFile, mode: "pdf" });
            return;
        }
        const allFiles = this.toPreviewFiles().filter((item) => item.isViewable && !item.isOffice);
        this.fileViewer.open(previewFile, allFiles);
    }

    onDownloadClick(file, ev) {
        ev.stopPropagation();
    }

    getHoverPreviewUrl(file) {
        const preview = toPreviewFile(file);
        if (preview.isImage) {
            return url(preview.urlRoute, preview.urlQueryParams);
        }
        if (preview.isPdf || preview.isOffice) {
            return this.getThumbnailUrl(file);
        }
        return false;
    }

    onHoverEnter(file) {
        this.hoverFileId = file.id;
    }

    onHoverLeave() {
        this.hoverFileId = null;
    }

    isHovered(file) {
        return this.hoverFileId === file.id;
    }
}

export const rnAttachmentPreviewField = {
    ...many2ManyBinaryField,
    component: RnAttachmentPreviewField,
};

registry.category("fields").add("rn_attachment_preview", rnAttachmentPreviewField);
