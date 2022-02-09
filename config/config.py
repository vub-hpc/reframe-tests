import git
import os

# log to syslog only with vsc10001 account
if os.getenv('USER') == 'vsc10001':
    syslog_level = 'info'
else:
    syslog_level = 'warning'

try:
    repo = git.Repo(os.path.join(os.getcwd(), os.pardir))
    commit = repo.git.rev_parse(repo.head.commit.hexsha, short=7)
except Exception:
    commit = ''

# use 'local' to run locally (or select partition with 'local' partition)
scheduler = 'slurm'

perf_logging_format = 'reframe: ' + '|'.join(
    [
        'username=%(osuser)s',
        'version=%(version)s',
        f'commit={commit}',
        'name=%(check_name)s',
        'system=%(check_system)s',
        'partition=%(check_partition)s',
        'environ=%(check_environ)s',
        'num_tasks=%(check_num_tasks)s',
        'num_cpus_per_task=%(check_num_cpus_per_task)s',
        'num_tasks_per_node=%(check_num_tasks_per_node)s',
        'modules=%(check_modules)s',
        'jobid=%(check_jobid)s',
        'perf_var=%(check_perf_var)s',
        'perf_value=%(check_perf_value)s',
        'unit=%(check_perf_unit)s',
    ]
)

environs_cpu = [
    'builtin',
    'foss-2019b',
    'intel-2019b',
    'foss-2020a',
    'intel-2020a',
    'foss-2020b',
    'intel-2020b',
    'foss-2021a',
    'intel-2021a',
]

environs_gpu = [
    'fosscuda-2019b',
    'fosscuda-2020a',
]

site_configuration = {
    'systems': [
        {
            'name': 'hydra',
            'descr': 'Hydra',
            'hostnames': ['login1.cerberus.os', 'login2.cerberus.os', '.*hydra.*'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'local',
                    'scheduler': 'local',
                    'modules': [],
                    'access': [],
                    'environs': environs_cpu,
                    'descr': 'tests in the local node (no job)',
                    'max_jobs': 1,
                    'launcher': 'local',
                },
                {
                    'name': 'skylake-sn',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=skylake,skylake_mpi'],
                    'environs': environs_cpu,
                    'descr': 'single-node jobs in Skylake nodes',
                    'max_jobs': 10,
                    'launcher': 'local',
                },
                {
                    'name': 'skylake-sn-mpi',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=skylake,skylake_mpi'],
                    'environs': environs_cpu,
                    'descr': 'single-node MPI jobs in Skylake nodes',
                    'max_jobs': 10,
                    'launcher': 'srun',
                },
                {
                    'name': 'skylake-mn-mpi-ib',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=skylake_mpi'],
                    'environs': environs_cpu,
                    'descr': 'multi-node MPI jobs in Skylake nodes with infiniband',
                    'max_jobs': 1,
                    'launcher': 'srun',
                },
                {
                    'name': 'skylake-mn-mpi-eth',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=skylake'],
                    'environs': environs_cpu,
                    'descr': 'multi-node MPI jobs in Skylake nodes without infiniband',
                    'max_jobs': 1,
                    'launcher': 'srun',
                },
                {
                    'name': 'broadwell-sn',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=broadwell'],
                    'environs': environs_cpu,
                    'descr': 'single-node jobs in Broadwell nodes',
                    'max_jobs': 10,
                    'launcher': 'local',
                },
                {
                    'name': 'broadwell-mpi',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=broadwell'],
                    'environs': environs_cpu,
                    'descr': 'MPI jobs in Broadwell nodes',
                    'max_jobs': 10,
                    'launcher': 'srun',
                },
                {
                    'name': 'ivybridge-sn',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=ivybridge_mpi'],
                    'environs': environs_cpu,
                    'descr': 'single-node jobs in Ivybridge nodes',
                    'max_jobs': 10,
                    'launcher': 'local',
                },
                {
                    'name': 'ivybridge-mpi',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=ivybridge_mpi'],
                    'environs': environs_cpu,
                    'descr': 'MPI jobs in Ivybrdige nodes',
                    'max_jobs': 1,
                    'launcher': 'srun',
                },
                {
                    'name': 'broadwell-pascal-sn',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=pascal_gpu'],
                    'environs': environs_cpu + environs_gpu,
                    'descr': 'single-node jobs in Broadwell nodes with Pascal P100 GPUs',
                    'max_jobs': 1,
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gres=gpu:{num_gpus_per_node}'],
                        },
                    ],
                    'launcher': 'local',
                },
                {
                    'name': 'zen2-ampere-sn',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': ['--partition=ampere_gpu'],
                    'environs': environs_cpu + environs_gpu,
                    'descr': 'single-node jobs in Zen2 nodes with Ampere A100 GPUs',
                    'max_jobs': 1,
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gres=gpu:{num_gpus_per_node}'],
                        },
                    ],
                    'launcher': 'local',
                },
                {
                    'name': 'ivybridge-kepler',
                    'scheduler': scheduler,
                    'modules': [],
                    'access': [],
                    'access': ['--partition=kepler_gpu'],
                    'environs': environs_cpu + environs_gpu,
                    'descr': 'single-node jobs in Ivybridge nodes with Kepler K20 GPUs',
                    'max_jobs': 1,
                    'resources': [
                        {
                            'name': 'gpu',
                            'options': ['--gres=gpu:{num_gpus_per_node}'],
                        },
                    ],
                    'launcher': 'local',
                },
            ],
        },
        {
            'name': 'chimera',
            'descr': 'Chimera',
            'hostnames': ['login1.cerberus.os', 'login2.cerberus.os', '.*chimera.*'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'haswell',
                    'scheduler': scheduler,
                    'modules': ['cluster/chimera'],
                    'access': [],
                    'environs': environs_cpu,
                    'descr': 'single-node jobs in Haswell nodes',
                    'max_jobs': 1,
                    'launcher': 'local',
                },
                {
                    'name': 'broadwell',
                    'scheduler': scheduler,
                    'modules': ['cluster/chimera'],
                    'access': [],
                    'environs': environs_cpu,
                    'descr': 'single-node jobs in Broadwell nodes',
                    'max_jobs': 1,
                    'launcher': 'local',
                },
                {
                    'name': 'haswell-mpi',
                    'scheduler': scheduler,
                    'modules': ['cluster/chimera'],
                    'access': [],
                    'environs': environs_cpu,
                    'descr': 'MPI jobs in Haswell nodes',
                    'max_jobs': 1,
                    'launcher': 'srun',
                },
                {
                    'name': 'broadwell-mpi',
                    'scheduler': scheduler,
                    'modules': ['cluster/chimera'],
                    'access': [],
                    'environs': environs_cpu,
                    'descr': 'MPI jobs in Broadwell nodes',
                    'max_jobs': 1,
                    'launcher': 'srun',
                },
            ],
        },
    ],
    'schedulers': [
        {
            'name': 'slurm',
            'use_nodes_option': True,  # always add --nodes Slurm option
        },
    ],
    'environments': [
        {'name': 'builtin', 'cc': 'gcc', 'cxx': 'g++', 'ftn': 'gfortran',},
        {
            'name': 'foss-2019b',
            'modules': ['foss/2019b', 'Autotools/20180311-GCCcore-8.3.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
        {
            'name': 'intel-2019b',
            'modules': ['intel/2019b', 'Autotools/20180311-GCCcore-8.3.0'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort',
        },
        {
            'name': 'foss-2020a',
            'modules': ['foss/2020a', 'Autotools/20180311-GCCcore-9.3.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
        {
            'name': 'intel-2020a',
            'modules': ['intel/2020a', 'Autotools/20180311-GCCcore-9.3.0'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort',
        },
        {
            'name': 'foss-2020b',
            'modules': ['foss/2020b', 'Autotools/20200321-GCCcore-10.2.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
        {
            'name': 'intel-2020b',
            'modules': ['intel/2020b', 'Autotools/20200321-GCCcore-10.2.0'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort',
        },
        {
            'name': 'foss-2021a',
            'modules': ['foss/2021a', 'Autotools/20210128-GCCcore-10.3.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
        {
            'name': 'intel-2021a',
            'modules': ['intel/2021a', 'Autotools/20210128-GCCcore-10.3.0'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort',
        },
        {
            'name': 'fosscuda-2019b',
            'modules': ['fosscuda/2019b', 'Autotools/20180311-GCCcore-8.3.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
        {
            'name': 'fosscuda-2020a',
            'modules': ['fosscuda/2020a', 'Autotools/20180311-GCCcore-9.3.0'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
        },
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'file',
                    'name': 'reframe.log',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_name)s: %(message)s',  # noqa: E501
                    'append': False,
                },
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s',
                },
                {
                    'type': 'file',
                    'name': 'reframe.out',
                    'level': 'info',
                    'format': '%(message)s',
                    'append': False,
                },
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': '%(check_job_completion_time)s ' + perf_logging_format,
                    'append': True,
                },
                {
                    'type': 'syslog',
                    'address': '/dev/log',
                    'level': syslog_level,
                    'format': perf_logging_format,
                    'append': True,
                },
            ],
        }
    ],
    'general': [
        {
            'check_search_path': ['checks/'],
            'check_search_recursive': True,
            'purge_environment': True,
            'resolve_module_conflicts': False,  # avoid loading the module before submitting the job
            'keep_stage_files': True,
        }
    ],
}
