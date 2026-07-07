import random

class RandomFloat:
    """ComfyUI node: returns a random float.

    Inputs:
      - min_val (float): minimum value (default 0.05).
      - max_val (float): maximum value (default 0.15).
      - seed (int): используемое зерно генерации. При fixed=False сюда записывается
            реально использованный случайный seed (сохраняется в workflow).
      - fixed (bool): если True — использовать запомненный seed (воспроизводимо);
            если False — генерировать новый случайный seed каждый запуск.
      - out_last_value (bool): если True, нода выдаёт last_value без генерации.
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
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "label": "Seed"
                }),
                "fixed": ("BOOLEAN", {
                    "default": False,
                    "label": "Fixed"
                }),
                "out_last_value": ("BOOLEAN", {
                    "default": False,
                    "label": "Out Last Value"
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
    def IS_CHANGED(cls, min_val, max_val, seed, fixed, out_last_value, last_value, run_count):
        # out_last_value → результат зависит только от last_value
        if out_last_value:
            return last_value
        # fixed=False → всегда пересчитываем (nan = нода не кешируется)
        if not fixed:
            return float("nan")
        # fixed=True → результат детерминирован запомненным seed
        return seed

    def generate(self, min_val, max_val, seed, fixed, out_last_value, last_value, run_count):
        # если включен режим out_last_value → вернуть текущее значение last_value без генерации
        if out_last_value:
            value = round(last_value, 5)
            RandomFloat.last_value = value
            return {
                "ui": {"last_value": [value], "run_count": [RandomFloat.run_count], "seed": [seed]},
                "result": (value,),
            }

        # нормализация диапазона
        if min_val > max_val:
            min_val, max_val = max_val, min_val

        # если не fixed → сгенерировать новый случайный seed и запомнить его
        if not fixed:
            seed = random.randint(0, 2147483647)

        # генерация по seed (воспроизводимо)
        rnd = random.Random(seed)
        value = rnd.uniform(min_val, max_val)

        # сохранить и округлить до пяти знаков
        RandomFloat.last_value = round(value, 5)
        RandomFloat.run_count += 1

        # обновить виджеты напрямую через значения полей
        # seed возвращается в UI, чтобы использованное зерно сохранилось в workflow
        return {
            "ui": {
                "last_value": [RandomFloat.last_value],
                "run_count": [RandomFloat.run_count],
                "seed": [seed],
            },
            "result": (RandomFloat.last_value,),
        }


NODE_CLASS_MAPPINGS = {"RandomFloatFox": RandomFloat}
NODE_DISPLAY_NAME_MAPPINGS = {"RandomFloatFox": "Random Float fox"}
