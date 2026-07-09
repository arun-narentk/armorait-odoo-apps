/** @odoo-module **/

async function callExperienceAssistant(query) {
    const response = await fetch("/my/experience/assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: { query },
            id: Date.now(),
        }),
    });
    const payload = await response.json();
    return payload.result || {};
}

function initExperienceAssistant(root) {
    const input = root.querySelector(".rn-exp-assistant-input");
    const button = root.querySelector(".rn-exp-assistant-send");
    const answer = root.querySelector(".rn-exp-assistant-answer");
    if (!input || !button || !answer) {
        return;
    }
    const ask = async () => {
        const query = input.value.trim();
        if (!query) {
            return;
        }
        answer.textContent = "Thinking...";
        const result = await callExperienceAssistant(query);
        answer.textContent = "";
        answer.appendChild(document.createTextNode(result.answer || "No answer available."));
        if (result.action && result.action.url) {
            const link = document.createElement("a");
            link.href = result.action.url;
            link.className = "d-block mt-2";
            link.textContent = "Open related section";
            answer.appendChild(document.createElement("br"));
            answer.appendChild(link);
        }
    };
    button.addEventListener("click", ask);
    input.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
            ev.preventDefault();
            ask();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".rn-experience-portal").forEach(initExperienceAssistant);
});
