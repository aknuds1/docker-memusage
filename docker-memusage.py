#!/usr/bin/env python
from collections import OrderedDict
import os.path
import re


def parse_mem_file(filename):
    data = OrderedDict()
    with open(filename, 'rb') as f:
        for line in f:
            splittage = line.split(':')
            data[splittage[0]] = splittage[1].strip()
    return data


def get_system_mem_usage():
    """Return the information in /proc/meminfo
    as a dictionary."""
    return parse_mem_file('/proc/meminfo')


def get_process_mem_usage():
    re_pid = re.compile(r'^\d+$')
    re_mem = re.compile(r'^(\d+) .+$')
    pid2usage = {}
    for pid in [d for d in os.listdir('/proc') if re_pid.match(d)]:
        fpath = os.path.join('/proc', pid, 'status')
        try:
            data = parse_mem_file(fpath)
        except IOError:
            continue

        try:
            name = data['Name']
            pid2usage[(pid, name)] = {
                'VmRSS': int(re_mem.match(data['VmRSS']).group(1)) / 1000.,
                'VmSwap': int(re_mem.match(data['VmSwap']).group(1)) / 1000.,
            }
        except KeyError:
            continue

    return OrderedDict(
        sorted(pid2usage.iteritems(), key=lambda x: x[1], reverse=True))


pid2usage = get_process_mem_usage()
total_usage = sum(pid2usage.values())
print('Total memory usage: {:.2f} MB'.format(total_usage))
for pid_etc, usage in pid2usage.iteritems():
    [pid, name] = pid_etc
    print('{} ({}): {:.2f} MB'.format(name, pid, usage))
