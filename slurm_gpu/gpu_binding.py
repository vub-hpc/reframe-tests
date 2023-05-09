#!/usr/bin/env python3
"""
script to calculate GPU binding

author: Samuel Moors (Vrije Universiteit Brussel)
"""
import json
import math
import os
import pynvml


def gpu_cpu_affinity(gpuid):
    """
    get GPU-CPU affinity
    @param gpuid: GPU device index as determined by nvml
    returns a list of allocated CPU ids that are on the same socket as gpuid
    """
    # pynvml.nvmlDeviceGetCpuAffinity returns an array of unsigned ints (sized to cpusetsize) of bitmasks
    # with the ideal CPU affinity for the device
    # cpuset = array reference in which to return a bitmask of CPUs, 64 CPUs per unsigned long on 64-bit machines
    # cpusetsize = size of the cpuset array that is safe to access
    # https://docs.nvidia.com/deploy/nvml-api/group__nvmlAffinity.html#group__nvmlAffinity
    cpusetsize = math.ceil(os.cpu_count() / 64)
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpuid)
    aff_str = ''
    for c_aff in pynvml.nvmlDeviceGetCpuAffinity(handle, cpusetsize):
        # c_aff is a 64-bit int
        aff_str = f'{c_aff:064b}{aff_str}'
    aff_list = [int(x) for x in reversed(aff_str)]

    return [i for i, aff in enumerate(aff_list) if aff != 0]


def main():
    "main function"
    pynvml.nvmlInit()

    gpubind = {'alloc_cpus': list(os.sched_getaffinity(0))}

    for gpuid in range(pynvml.nvmlDeviceGetCount()):
        gpubind[f'affinity_gpu_{gpuid}'] = gpu_cpu_affinity(gpuid)

    with open('gpu_binding.json', 'w', encoding='utf-8') as json_file:
        json.dump(gpubind, json_file)

    pynvml.nvmlShutdown()


if __name__ == '__main__':
    main()
