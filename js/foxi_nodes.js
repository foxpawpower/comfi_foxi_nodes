import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Foxi.RandomFloat",
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

            // записываем реально использованный seed обратно в виджет,
            // чтобы он сохранился в workflow и мог быть воспроизведён через Fixed
            if (message.seed !== undefined) {
                const w = this.widgets?.find(w => w.name === "seed");
                if (w) w.value = message.seed[0];
            }

            app.graph?.setDirtyCanvas(true, true);
        };
    },
});
