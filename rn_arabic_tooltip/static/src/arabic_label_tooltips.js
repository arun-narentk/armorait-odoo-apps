import { registry } from "@web/core/registry";

const LABEL_SELECTOR = [
    ".o_form_label",
    ".o_field_label",
    ".o_wrap_label",
    ".o_notebook_headers .nav-link",
    ".o_list_table th",
    "label",
].join(",");

const IGNORED_LABELS = new Set(["", "?", "#"]);

function cleanLabel(text) {
    return (text || "")
        .replace(/\s+/g, " ")
        .replace(/\s*[:：]\s*$/, "")
        .replace(/\s*\*\s*$/, "")
        .trim();
}

function isUsefulLabel(text) {
    if (!text || IGNORED_LABELS.has(text)) {
        return false;
    }
    if (text.length > 45) {
        return false;
    }
    // Skip mostly numeric table headers or values.
    if (/^[\d\s.,/%-]+$/.test(text)) {
        return false;
    }
    return /[A-Za-z]/.test(text);
}

class ArabicLabelTooltipService {
    constructor(env, services) {
        this.orm = services.orm;
        this.cache = new Map();
        this.pending = new Set();
        this.timer = null;
        this.observer = null;
        this.start();
    }

    start() {
        this.scheduleScan();
        this.observer = new MutationObserver(() => this.scheduleScan());
        this.observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    scheduleScan() {
        window.clearTimeout(this.timer);
        this.timer = window.setTimeout(() => this.scan(), 300);
    }

    async scan() {
        const elements = [...document.querySelectorAll(LABEL_SELECTOR)];
        const missing = new Set();

        for (const el of elements) {
            // Screens that ship their own OWL tooltip opt out via this class,
            // so we never apply browser title tooltips inside them.
            if (el.closest(".o_rn_dashboard")) {
                continue;
            }
            const label = cleanLabel(el.textContent);
            if (!isUsefulLabel(label)) {
                continue;
            }
            el.dataset.rnTooltipSource = label;
            if (this.cache.has(label)) {
                this.applyTooltip(el, this.cache.get(label));
            } else if (!this.pending.has(label)) {
                missing.add(label);
                this.pending.add(label);
            }
        }

        if (!missing.size) {
            return;
        }

        try {
            const translations = await this.orm.call(
                "rn.arabic.tooltip",
                "get_arabic_label_translations",
                [[...missing]]
            );
            for (const label of missing) {
                this.cache.set(label, translations[label] || null);
                this.pending.delete(label);
            }
            this.applyCachedTooltips();
        } catch {
            for (const label of missing) {
                this.pending.delete(label);
            }
        }
    }

    applyCachedTooltips() {
        for (const el of document.querySelectorAll("[data-rn-tooltip-source]")) {
            const label = el.dataset.rnTooltipSource;
            if (this.cache.has(label)) {
                this.applyTooltip(el, this.cache.get(label));
            }
        }
    }

    applyTooltip(el, translation) {
        if (!translation) {
            return;
        }
        if (!el.dataset.rnOriginalTitle && el.hasAttribute("title")) {
            el.dataset.rnOriginalTitle = el.getAttribute("title");
        }
        el.setAttribute("title", translation);
        el.dataset.rnArabicTooltip = translation;
    }
}

export const arabicLabelTooltipService = {
    dependencies: ["orm"],
    start(env, services) {
        return new ArabicLabelTooltipService(env, services);
    },
};

registry.category("services").add("rn_arabic_label_tooltips", arabicLabelTooltipService);
