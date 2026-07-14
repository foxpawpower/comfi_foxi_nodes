import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// запросить у сервера истинное значение для текущих seed/min/max
// и подставить его в last_value (тот же алгоритм, что и в generate).
// инвариант: last_value всегда показывает число, которое даст Run
// с текущими значениями виджетов
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

// дебаунс, чтобы серия изменений (загрузка workflow задаёт все виджеты
// подряд) вылилась в один запрос
function scheduleRefresh(node) {
    clearTimeout(node._foxiRefreshTimer);
    node._foxiRefreshTimer = setTimeout(() => refreshLastValue(node), 100);
}

// перехват записи в widget.value: ловит и ручное редактирование, и
// программные изменения (randomize/increment из control_after_generate)
function hookWidget(node, name) {
    const w = node.widgets?.find(w => w.name === name);
    if (!w || w._foxiHooked) return;
    w._foxiHooked = true;
    let val = w.value;
    Object.defineProperty(w, "value", {
        configurable: true,
        get() { return val; },
        set(v) {
            val = v;
            scheduleRefresh(node);
        },
    });
}

app.registerExtension({
    name: "Foxi.RandomFloat",

    // при загрузке workflow (в т.ч. из PNG) пересчитать last_value из
    // сохранённого seed — сохранённое значение может быть устаревшим
    loadedGraphNode(node) {
        if (node.comfyClass !== "RandomFloatFox") return;
        scheduleRefresh(node);
    },

    async nodeCreated(node) {
        if (node.comfyClass !== "RandomFloatFox") return;

        hookWidget(node, "min_val");
        hookWidget(node, "max_val");
        hookWidget(node, "seed");

        const onExecuted = node.onExecuted;
        node.onExecuted = function (message) {
            if (onExecuted) onExecuted.call(this, message);

            if (message.run_count !== undefined) {
                const w = this.widgets?.find(w => w.name === "run_count");
                if (w) w.value = message.run_count[0];
            }

            // last_value здесь не трогаем: им управляет refreshLastValue,
            // который срабатывает на каждое изменение seed/min/max —
            // в том числе когда control_after_generate рандомизирует seed
            // после генерации

            app.graph?.setDirtyCanvas(true, true);
        };
    },
});
