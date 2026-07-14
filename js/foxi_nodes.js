import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// запросить у сервера истинное значение для текущих seed/min/max
// и подставить его в last_value (тот же алгоритм, что и в generate)
async function refreshLastValue(node) {
    const get = (name) => node.widgets?.find(w => w.name === name);
    const minW = get("min_val");
    const maxW = get("max_val");
    const seedW = get("seed");
    const lastW = get("last_value");
    if (!minW || !maxW || !seedW || !lastW) return;

    try {
        const resp = await api.fetchApi("/foxi/random_float", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                min_val: minW.value,
                max_val: maxW.value,
                seed: seedW.value,
            }),
        });
        const data = await resp.json();
        if (data.value !== undefined) {
            lastW.value = data.value;
            app.graph?.setDirtyCanvas(true, true);
        }
    } catch (e) {
        console.warn("[FoxiRandomFloat] refreshLastValue failed:", e);
    }
}

app.registerExtension({
    name: "Foxi.RandomFloat",

    // вызывается для каждой ноды при загрузке workflow (в т.ч. из PNG):
    // сохранённое last_value может быть устаревшим (снимок делается до
    // выполнения), поэтому пересчитываем его из сохранённого seed
    loadedGraphNode(node) {
        if (node.comfyClass !== "RandomFloatFox") return;
        refreshLastValue(node);
    },

    async nodeCreated(node) {
        if (node.comfyClass !== "RandomFloatFox") return;

        const onExecuted = node.onExecuted;
        node.onExecuted = function (message) {
            if (onExecuted) onExecuted.call(this, message);

            console.log("[FoxiRandomFloat] onExecuted message:", message);

            if (message.last_value !== undefined) {
                const w = this.widgets?.find(w => w.name === "last_value");
                if (w) w.value = message.last_value[0];
            }

            if (message.run_count !== undefined) {
                const w = this.widgets?.find(w => w.name === "run_count");
                if (w) w.value = message.run_count[0];
            }

            app.graph?.setDirtyCanvas(true, true);
        };
    },
});
