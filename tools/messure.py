import time
# import wrapper
from functools import wraps, partial


def cronometro(func):
    """Decorador para contabilizar el tiempo de ejecución de una función"""

    def wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        final_time = round(time_end - time_start, 2)
        print(f"Tiempo de ejecución de {func.__name__}: {final_time} seg")
        return result

    return wrapper








