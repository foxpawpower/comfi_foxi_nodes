import random

class RandomFloat:
    """ComfyUI node: returns a random float.

    Inputs:
      - min_val (float): minimum value (default 0.05).
      - max_val (float): maximum value (default 0.15).
      - seed (int): optional seed; -1 = random, любое другое число = детерминированный результат.
      - hold_last (bool): если True, нода выдаёт последнее число без генерации.
    """

    last_value = None  # хранение последнего сгенерированного числа

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_val": ("FLOAT", {
                    "default":  0.05,
                    "min": -1e9,
                    "max": 1e9,
                    "step": 0.01,
                    "label": "Min"
                }),
                "max_val": ("FLOAT", {
                    "default": 0.15,
                    "min": -1e9,
                    "max": 1e9,
                    "step": 0.01,
                    "label": "Max"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "label": "Seed (-1=random)"
                }),
                "hold_last": ("BOOLEAN", {
                    "default": False,
                    "label": "Hold Last Value"
                }),
            }
        }

    # теперь возвращаем два значения: само число и last_value для UI
    RETURN_TYPES = ("FLOAT", "FLOAT",)
    RETURN_NAMES = ("value", "last_value",)
    FUNCTION = "generate"
    CATEGORY = "Foxi/Custom"

    def generate(self, min_val, max_val, seed, hold_last):
        # если включен режим "hold_last" → просто вернуть сохранённое число
        if hold_last and RandomFloat.last_value is not None:
            return (RandomFloat.last_value, RandomFloat.last_value)

        # нормализация диапазона
        if min_val > max_val:
            min_val, max_val = max_val, min_val

        # генерация нового числа
        if seed is None or seed < 0:
            value = random.uniform(min_val, max_val)
        else:
            rnd = random.Random(seed)
            value = rnd.uniform(min_val, max_val)

        # сохранить и округлить до сотых
        RandomFloat.last_value = round(value, 2)
        return (RandomFloat.last_value, RandomFloat.last_value)


NODE_CLASS_MAPPINGS = {"RandomFloat": RandomFloat}
NODE_DISPLAY_NAME_MAPPINGS = {"RandomFloat": "Random Float"}
