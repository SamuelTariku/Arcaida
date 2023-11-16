import re
import humanize
from datetime import datetime, timedelta


regex = re.compile(
    r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_time(time_str):
    print(time_str)
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

    if (addedTime == None):
        return

    return currentDate + addedTime


def convertDate(date, past=True, verbose=True):
    if(past):
        delta = datetime.now() - date
    else:
        delta = date - datetime.now()
    
    if(verbose):
        return humanize.naturaltime(delta)
    else:
        return humanize.naturaldelta(delta)
