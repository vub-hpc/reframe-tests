#!/usr/bin/env python3
"""
script to calculate GPU binding

author: Samuel Moors (Vrije Universiteit Brussel)
"""
import math
import os
import pynvml
import json


def gpu_cpu_affinity(gpuid):
    """
    get GPU-CPU affinity
    returns a list of allocated CPU ids that are on the same socket as gpuid
    """
    cpusetsize = math.ceil(os.cpu_count() / 64)
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpuid)
    aff_str = ''
    for c_aff in pynvml.nvmlDeviceGetCpuAffinity(handle, cpusetsize):
        aff_string = f'{c_aff:064b}{aff_str}'
    aff_list = [int(x) for x in reversed(aff_string)]

    return [i for i, aff in enumerate(aff_list) if aff != 0]


if __name__ == '__main__':
    pynvml.nvmlInit()

    gpubind = {'alloc_cpus': list(os.sched_getaffinity(0))}

    for gpuid in range(pynvml.nvmlDeviceGetCount()):
        gpubind[f'affinity_gpu_{gpuid}'] = gpu_cpu_affinity(gpuid)

    json.dump(gpubind, open('gpu_binding.json', 'w'))

    pynvml.nvmlShutdown()
