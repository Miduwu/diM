import re
import pydash as _

s = 1000
m = s * 60
h = m * 60
d = h * 24
w = d * 7
mo = d * 30
y = d * 365.25

dick = {
    "ms": { "value": 1, "full": "milisecond" },
    "s": { "value": s, "full": "second" },
    "m": { "value": m, "full": "minute" },
    "h": { "value": h, "full": "hour" },
    "d": { "value": d, "full": "day" },
    "w": { "value": w, "full": "week" },
    "mo": { "value": mo, "full": "month" },
    "y": { "value": y, "full": "year" }
}

def parse(string):
    r = re.findall('(\d+\.\d+|\d+)(ms|s|mo|m|h|d|w|y)', string, flags=re.IGNORECASE)
    if not r:
        return None
    final = 0
    for datuple in r:
        TIME, TYPE = datuple
        final += float(TIME) * dick[TYPE.lower()]["value"]
    return final

def ms_to_short(number):
    absed = abs(number)
    for key in list(dick.keys())[::-1]:
        if absed >= dick[key]["value"]:
            return f'{round(number / dick[key]["value"])}{key}'
        else:
            continue

def ms_to_long(number):
    absed = abs(number)
    for key in (list(dick.keys())[::-1]):
        if absed >= dick[key]["value"]:
            return pluralify(number, absed, dick[key]["value"], dick[key]["full"])
        else:
            continue

def pluralify(ms, absed, x, name):
    see = absed >= x * 1.5
    return f'{round(ms / x)} {name}{"s" if see else ""}'

def load(time: str | int | float, long = False):
    if isinstance(time, str):
        return parse(time)
    else:
        return ms_to_long(time) if long else ms_to_short(time)