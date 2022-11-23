#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter
import os
from pprint import pprint
import sys
import textwrap


class CustomFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    pass


parser = ArgumentParser(
    formatter_class=CustomFormatter,
    epilog='''
* options '--checkpath' and '--name' correspond to the ReFrame options with the same name
* options '--system' and '--partitions' set ReFrame options '--system' and '--setvar valid_systems='
* option '--valid_prog_environs' sets ReFrame option '--setvar valid_prog_environs='

any additional options not listed here are passed directly to ReFrame
''',
)

parser.add_argument('-c', '--checkpath', dest='checkpath', required=True,
                    help='path (relative to this script) of test directory or script')
parser.add_argument('-n', '--name', dest='name',
                    help='check name')
parser.add_argument('--system', dest='system', choices=['hydra', 'chimera', 'manticore', 'local'],
                    default='hydra', help='run tests in given cluster')
parser.add_argument('--partitions', dest='partitions',
                    help='comma-separated list of ReFrame partitions')
parser.add_argument('--valid_prog_environs', dest='valid_prog_environs',
                    help='comma-separated list of programming environments')

args, extra_args = parser.parse_known_args()

system = args.system
checkpath = args.checkpath
name = args.name

tests = [
    {
        'checkpath': 'blas-tester',
        'valid_prog_environs': ['foss-2021a', 'intel-2021a'],
        'valid_systems': {
            'hydra': ['hydra:skylake-sn', 'hydra:broadwell-sn', 'hydra:ivybridge-sn'],
            'chimera': ['chimera:broadwell-sn', 'chimera:haswell-sn'],
            'manticore': ['manticore:skylake-sn', 'manticore:ivybridge-sn'],
            'local': ['local:local'],
        },
        'setvar_extra': {
            'num_cpus_per_task': '4',
            'BLASTest.exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'cp2k_tests',
        'name': 'CP2KTestSingleNode',
        'valid_systems': {
            'hydra': ['hydra:skylake-sn-mpi', 'hydra:broadwell-mpi', 'hydra:ivybridge-mpi'],
            'chimera': ['chimera:broadwell-mpi', 'chimera:haswell-mpi'],
            'manticore': ['manticore:skylake-mpi', 'manticore:ivybridge-mpi'],
            'local': ['local:local'],
        },
        'setvar_extra': {
            'modules': 'CP2K/7.1-intel-2020a',
            'num_tasks': '4',
            'num_tasks_per_node': '4',
            'exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'cp2k_tests',
        'name': 'CP2KTestMultiNode',
        'valid_systems': {
            'hydra': ['hydra:skylake-mn-mpi-ib', 'hydra:ivybridge-mpi'],
            'chimera': ['chimera:broadwell-mpi', 'chimera:haswell-mpi'],
            'local': ['local:local-mpi'],
        },
        'setvar_extra': {
            'modules': 'CP2K/7.1-intel-2020a',
            'num_tasks': '4',
            'num_tasks_per_node': '1',
            'exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'gromacs_bench',
        'name': 'GMXBenchMEMMultiNode',
        'valid_systems': {
            'hydra': ['hydra:skylake-mn-mpi-ib', 'hydra:ivybridge-mpi'],
            'chimera': ['chimera:broadwell-mpi', 'chimera:haswell-mpi'],
            'local': ['local:local-mpi'],
        },
        'setvar_extra': {
            'modules': 'GROMACS/2021.3-foss-2021a',
            'num_tasks': '4',
            'num_tasks_per_node': '1',
            'exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'gromacs_bench',
        'name': 'GMXBenchMEMSingleNode',
        'valid_systems': {
            'hydra': ['hydra:skylake-sn', 'hydra:broadwell-sn', 'hydra:ivybridge-sn'],
            'chimera': ['chimera:broadwell-sn', 'chimera:haswell-sn'],
            'manticore': ['manticore:skylake-sn', 'manticore-ivybridge-sn'],
            'local': ['local:local'],
        },
        'setvar_extra': {
            'modules': 'GROMACS/2021.3-foss-2021a',
            'num_cpus_per_task': '4',
            'exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'gromacs_bench',
        'name': 'GMXBenchMEMSingleNodeGPU',
        'valid_systems': {
            'hydra': ['hydra:zen2-ampere-sn-gpu', 'hydra:broadwell-pascal-sn-gpu'],
            'local': ['local:local'],
        },
        'setvar_extra': {
            'modules': 'GROMACS/2021.3-foss-2021a-CUDA-11.3.1',
            'num_cpus_per_task': '4',
            'num_gpus_per_node': '1',
            'exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
        },
    },
    {
        'checkpath': 'ior',
        'valid_prog_environs': ['foss-2021a'],
        'valid_systems': {
            'hydra': ['hydra:skylake-mn-mpi-ib', 'hydra:skylake-mn-mpi-eth'],
            'local': ['local:local-mpi']
        },
        'setvar_extra': {
            'iorBuildTest.num_cpus_per_task': '4',
            'iorWriteTest.num_tasks': '4',
            'iorReadTest.num_tasks': '4',
            'iorWriteTest.exclusive_access': 'false',
            'iorReadTest.exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
            'job-option': 'mem-per-cpu=4G'
        },
    },
    {
        'checkpath': 'lmod',
        'valid_systems': {
            'hydra': ['hydra:skylake-sn'],
            'manticore': ['manticore:skylake-sn'],
            'chimera': ['chimera:broadwell-sn'],
            'local': ['local:local'],
        },
    },
    {
        'checkpath': 'osu',
        'valid_prog_environs': ['foss-2021a', 'intel-2021a'],
        'valid_systems': {
            'hydra': ['hydra:skylake-mn-mpi-ib', 'hydra:ivybridge-mpi'],
            'manticore': ['manticore:skylake-mpi', 'manticore-ivybridge-mpi'],
            'chimera': ['chimera:broadwell-mpi', 'chimera:haswell-mpi'],
            'local': ['local:local-mpi'],
        },
        'setvar_extra': {
            'OSULatencyTest.num_tasks': '2',
            'OSUBandwidthTest.num_tasks': '2',
            'OSUBuildTest.num_cpus_per_task': '4',
            'OSULatencyTest.exclusive_access': 'false',
            'OSUBandwidthTest.exclusive_access': 'false',
        },
        'extra': {
            'exec-policy': 'serial',
            'tag': 'prod_small',
        },
    },
]

selected_tests = []
for test in tests:
    if checkpath.startswith(test['checkpath']):
        if not name or not test.get('name') or name == test.get('name'):
            selected_tests.append(test)

num_selected = len(selected_tests)
if num_selected != 1:
    print(f'ERROR: {num_selected} tests selected, exactly 1 is required. Add option --name to narrow selection.')
    pprint(selected_tests)
    sys.exit(1)

selected = selected_tests[0]

if args.partitions:
    partitions = args.partitions.split(',')
    valid_systems = [f'{system}:{x}' for x in partitions]
else:
    valid_systems = selected['valid_systems'][system]

if args.valid_prog_environs:
    valid_prog_environs = args.valid_prog_environs.split(',')
else:
    valid_prog_environs = selected.get('valid_prog_environs', ['builtin'])

name = selected.get('name') if not name else name

cmd = [
    'reframe --run',
    f'--checkpath {checkpath}',
    f'--name {name}' if name else '',
    f'--system {system}',
    f'--setvar valid_prog_environs={",".join(valid_prog_environs)}',
    f'--setvar valid_systems={",".join(valid_systems)}',
]

if selected.get('setvar_extra'):
    for key, val in selected['setvar_extra'].items():
        cmd.append(f'--setvar {key}={val}')

if selected.get('extra'):
    for key, val in selected['extra'].items():
        cmd.append(f'--{key} {val}')

cmd.extend(extra_args)

print(' '.join(cmd))
os.system(' '.join(cmd))
