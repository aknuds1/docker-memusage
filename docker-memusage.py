#!/usr/bin/env python
from collections import OrderedDict
from pprint import pprint
import os.path
import re
import sys


def parse_mem_file(filename):
    data = OrderedDict()
    with open(filename, 'rb') as f:
        for line in f:
            splittage = line.split(':')
            data[splittage[0]] = splittage[1].strip()
    return data


def meminfo():
    """Return the information in /proc/meminfo
    as a dictionary."""
    return parse_mem_file('/proc/meminfo')


def get_process_mem_usage():
    re_pid = re.compile(r'^\d+$')
    re_mem = re.compile(r'^(\d+) .+$')
    pid2usage = {}
    for pid in [d for d in os.listdir('/proc') if re_pid.match(d)]:
        fpath = os.path.join('/proc', pid, 'status')
        data = parse_mem_file(fpath)
        try:
            pid2usage[pid] = int(re_mem.match(data['VmHWM']).group(1)) / 1024.
        except KeyError:
            continue

    return OrderedDict(
        sorted(pid2usage.iteritems(), key=lambda x: x[1], reverse=True))

pid2usage = get_process_mem_usage()
total_usage = sum(pid2usage.values())
print('Total memory usage: {:.2f}'.format(total_usage))
for pid, usage in pid2usage.iteritems():
    print('{}: {:.2f} MB'.format(pid, usage))
