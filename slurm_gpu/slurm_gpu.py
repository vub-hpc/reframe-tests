import json
from pathlib import Path
import reframe as rfm
import reframe.utility.sanity as sn


TESTPATH = Path(__file__).parent


class SlurmGPUTestBase(rfm.RunOnlyRegressionTest):
    descr = "Slurm GPU test: "
    valid_systems = required
    valid_prog_environs = required
    time_limit = '10m'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_gpus_per_node = 1


@rfm.simple_test
class GPUBinding(SlurmGPUTestBase):
    descr += "allocated CPUs are on the same socket as the allocated GPU"
    modules = ['gpustat/1.1-GCCcore-11.3.0']
    num_cpus_per_task = 3
    executable = f'{TESTPATH}/gpu_binding.py'

    @run_after('init')
    def post_init(self):
        self.extra_resources = {
            'gpu': {'num_gpus_per_node': self.num_gpus_per_node},
        }

    @sanity_function
    def assert_affinity(self):
        gpubind = json.load(open('gpu_binding.json', 'r'))
        return sn.assert_eq(
            gpubind['alloc_cpus'],
            gpubind['affinity_gpu_0'],
            'allocated cpus {} should be equal to gpu-cpu affinity {1}'
        )
