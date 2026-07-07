import random

class RandomFloat:
    """ComfyUI node: returns a random float.

    Inputs:
      - min_val (float): minimum value (default 0.05).
      - max_val (float): maximum value (default 0.15).
      - seed (int): зерно генерации. ComfyUI сам добавляет рядом выпадающий
            control_after_generate (fixed / randomize / increment / decrement) —
            он и управляет тем, меняется seed между запусками или фиксируется.
      - last_value (float): поле только для отображения последнего числа (readonly).
    """

    last_value = None  # хранение последнего сгенерированного числа
    run_count = 0       # счётчик запусков

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_val": ("FLOAT", {
                    "default": 0.05,
                    "min": -1e9,
                    "max": 1e9,
                    "step": 0.00001,
                    "label": "Min"
                }),
                "max_val": ("FLOAT", {
                    "default": 0.15,
                    "min": -1e9,
                    "max": 1e9,
                    "step": 0.00001,
                    "label": "Max"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "label": "Seed"
                }),
                # поле для отображения числа
                "last_value": ("FLOAT", {
                    "default": 0.0,
                    "step": 0.00001,
                    "label": "Last Generated"
                }),
                # счётчик — обычный INT вход, значение устанавливается кодом через IS_CHANGED
                "run_count": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "label": "Run #"
                }),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "generate"
    CATEGORY = "Foxi/Custom"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, min_val, max_val, seed, last_value, run_count):
        # результат детерминирован seed; менять его между запусками —
        # задача control_after_generate (fixed → seed тот же, randomize → новый)
        return seed

    def generate(self, min_val, max_val, seed, last_value, run_count):
        # нормализация диапазона
        if min_val > max_val:
            min_val, max_val = max_val, min_val

        # генерация детерминирована seed → одинаковый seed = одинаковое число
        rnd = random.Random(seed)
        value = rnd.uniform(min_val, max_val)

        # сохранить и округлить до пяти знаков
        RandomFloat.last_value = round(value, 5)
        RandomFloat.run_count += 1

        # обновить виджеты напрямую через значения полей
        return {
            "ui": {
                "last_value": [RandomFloat.last_value],
                "run_count": [RandomFloat.run_count],
            },
            "result": (RandomFloat.last_value,),
        }


NODE_CLASS_MAPPINGS = {"RandomFloatFox": RandomFloat}
NODE_DISPLAY_NAME_MAPPINGS = {"RandomFloatFox": "Random Float fox"}
