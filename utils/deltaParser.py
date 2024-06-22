import re
import humanize
from string import Formatter
from datetime import datetime, timedelta


regex = re.compile(
    r"((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
)


def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def calculateDate(time_str):
    currentDate = datetime.now()
    addedTime = parse_time(time_str)

    if addedTime == timedelta():
        return
    print(currentDate, addedTime, currentDate + addedTime)
    return currentDate + addedTime


# def convertDate(date, past=True, verbose=True):
#     if past:
#         delta = datetime.now() - date
#     else:
#         delta = date - datetime.now()

#     if verbose:
#         return humanize.naturaltime(delta)
#     else:
#         return humanize.naturaldelta(delta)


def convertDate(date):
    delta = date - datetime.now()
    totalSeconds = delta.total_seconds()

    weeks, remainder = divmod(totalSeconds, 604800)
    days, remainder = divmod(totalSeconds, 86400)
    hours, remainder = divmod(totalSeconds, 3600)
    minutes, remainder = divmod(totalSeconds, 60)

    if weeks > 1:
        return "{}w".format(int(weeks))
    elif days > 1:
        return "{}d".format(int(days))
    elif hours > 1:
        return "{}h".format(int(hours))
    elif minutes > 1:
        return "{}m".format(int(minutes))
    elif totalSeconds > 1:
        return "{}s".format(totalSeconds)
    else:
        return "0s"
