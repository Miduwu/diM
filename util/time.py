import re

s = 1000
m = s * 60
h = m * 60
d = h * 24
w = d * 7
mo = d * 30
y = d * 365.25

def parse_time(string):
    r = re.match('^\d+(\.\d+)?(ms|s|mo|m|h|d|w|y)$', string, flags=re.IGNORECASE)
    if not r:
        return None
    r = r.group(0)
    number, _type = re.sub('[^\d\.]', '', r), re.sub('[\d\.]', '', r).lower()
    floated = float(number)
    if _type == 'ms':
        return floated
    elif _type == 's':
        return floated * s
    elif _type == 'm':
        return floated * m
    elif _type == 'h':
        return floated * h
    elif _type == 'd':
        return floated * d
    elif _type == 'w':
        return floated * w
    elif _type == 'mo':
        return floated * mo
    elif _type == 'y':
        return floated * y
    else:
        return None

def ms_to_short(number):
    absed = abs(number)
    if absed >= y:
        return f'{round(number / y)}y'
    if absed >= mo:
        return f'{round(number / mo)}mo'
    if absed >= w:
        return f'{round(number / d)}w'
    if absed >= d:
        return f'{round(number / d)}d'
    if absed >= h:
        return f'{round(number / h)}h'
    if absed >= m:
        return f'{round(number / m)}m'
    if absed >= s:
        return f'{round(number / s)}s'
    return f'{round(number)}ms'

def ms_to_long(number):
    absed = abs(number)
    if absed >= y:
        return pluralify(number, absed, y, 'year')
    if absed >= mo:
        return pluralify(number, absed, mo, 'month')
    if absed >= w:
        return pluralify(number, absed, w, 'week')
    if absed >= d:
        return pluralify(number, absed, d, 'day')
    if absed >= h:
        return pluralify(number, absed, h, 'hour')
    if absed >= m:
        return pluralify(number, absed, m, 'minute')
    if absed >= s:
        return pluralify(number, absed, s, 'second')
    return f'{number} miliseconds'

def pluralify(ms, absed, x, name):
    see = absed >= x * 1.5
    return f'{round(ms / x)} {name}{"s" if see else ""}'

def load(time: str | int | float, long = False):
    if isinstance(time, str):
        return parse_time(time)
    else:
        return ms_to_long(time) if long else ms_to_short(time)