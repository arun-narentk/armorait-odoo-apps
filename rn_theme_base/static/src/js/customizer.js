/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

function applyCustomizer(body) {
    const primary = body.dataset.tbPrimary || "#1a3a5c";
    const secondary = body.dataset.tbSecondary || "#2d7dd2";
    const accent = body.dataset.tbAccent || "#f4a261";
    const headingFont = body.dataset.tbHeadingFont || "Poppins";
    const bodyFont = body.dataset.tbBodyFont || "Inter";

    const root = document.documentElement;
    root.style.setProperty("--tb-primary", primary);
    root.style.setProperty("--tb-secondary", secondary);
    root.style.setProperty("--tb-accent", accent);
    root.style.setProperty("--tb-heading-font", `'${headingFont}', sans-serif`);
    root.style.setProperty("--tb-body-font", `'${bodyFont}', sans-serif`);

    if (body.dataset.tbStickyHeader === "1") {
        body.classList.add("tb-header-sticky");
    } else {
        body.classList.remove("tb-header-sticky");
    }

    if (body.dataset.tbAnimations === "0") {
        document.querySelectorAll(".tb-reveal, .tb-reveal-left, .tb-reveal-right").forEach((el) => {
            el.classList.add("tb-revealed");
        });
    }

    const wa = body.dataset.tbWhatsapp;
    if (wa) {
        document.querySelectorAll(".tb-whatsapp-btn[data-auto-link]").forEach((btn) => {
            btn.setAttribute("href", `https://wa.me/${wa}`);
        });
    }

    if (body.dataset.tbEmergency === "1") {
        const text = body.dataset.tbEmergencyText || "";
        let banner = document.querySelector(".tb-emergency-banner-global");
        if (!banner && text) {
            banner = document.createElement("div");
            banner.className = "tb-emergency-banner tb-emergency-banner-global";
            banner.setAttribute("role", "alert");
            banner.textContent = text;
            document.body.prepend(banner);
        } else if (banner) {
            banner.textContent = text;
            banner.style.display = text ? "" : "none";
        }
    }
}

export class TbCustomizer extends Interaction {
    static selector = "body";

    setup() {
        applyCustomizer(this.el);
        this.lazyImages();
    }

    lazyImages() {
        for (const img of document.querySelectorAll("#wrapwrap img:not([loading])")) {
            if (!img.closest("header") && !img.closest(".carousel-item.active")) {
                img.setAttribute("loading", "lazy");
                img.classList.add("tb-lazy-img");
            }
        }
    }
}

registry.category("public.interactions").add("rn_theme_base.customizer", TbCustomizer);
