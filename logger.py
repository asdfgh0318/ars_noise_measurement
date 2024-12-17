from datetime import datetime
from colorist import Color

STYLE_DEFAULT = Color.WHITE


def log_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log_time_name():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

log_file = open(f'logs/L-{log_time_name()}.txt', 'a')

def spr(x, style=STYLE_DEFAULT):
    print(f"[{log_time()}] {style}{x}{Color.OFF}")
    log_file.write(f'[{log_time()}] {x}\n')

def prefixed_spr(prefix, pr=spr):
    def ret(x, *args):
        pr(f"{prefix}: {x}", *args)
    return ret
