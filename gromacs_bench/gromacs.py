import os

import reframe as rfm
import reframe.utility.sanity as sn

homepage = 'https://www.mpibpc.mpg.de/grubmueller/bench'
src_name = 'benchMEM'
src_version = '20200626'
src_sha256 = '3c1c8cd4f274d532f48c4668e1490d389486850d6b3b258dfad4581aa11380a4'
src_dir = f'{src_name}-{src_version}'
src_url = 'https://www.mpibpc.mpg.de/15101317/benchMEM.zip'
src_path = os.path.join(os.environ['REFRAME_SOURCEPATH'], src_name[0].lower(), src_name, f'{src_dir}.zip')

download_cmd = f'wget {src_url} -O {src_path}'
checksum_cmd = f'sha256sum -c <(echo {src_sha256} {src_path})'
extract_cmd = f'mkdir {src_dir} && unzip {src_path} -d {src_dir} && cd {src_dir}'


class GMXBenchMEMBase(rfm.RunOnlyRegressionTest):
    """ base clase for BenchMEM test """
    descr = 'GROMACS benchMEM test'
    valid_systems = required
    valid_prog_environs = ['default']
    prerun_cmds = [
        download_cmd if not os.path.isfile(src_path) else '',
        checksum_cmd + ' && ' + extract_cmd,
    ]
    time_limit = '10m'
    executable_opts = ['-s', 'benchMEM.tpr', '-nsteps', '12000', '-resetstep', '7000']
    logfile = os.path.join(f'{src_dir}', 'md.log')
    modules = required
    exclusive_access = required

    @sanity_function
    def sanity_run(self):
        return sn.assert_found(r'^Finished mdrun', self.logfile)

    @performance_function('ns/day', perf_key='perf')
    def perf(self):
        return sn.extractsingle(rf'^Performance:\s+(\S+)\s+\S+', self.logfile, 1, float)


@rfm.simple_test
class GMXBenchMEMSingleNode(GMXBenchMEMBase):
    descr += ' single node, multi-core'
    executable = 'gmx mdrun'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = required

    @run_after('init')
    def post_init(self):
        self.executable_opts += ['-nt', f'{self.num_cpus_per_task}']
        self.env_vars = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
        }


@rfm.simple_test
class GMXBenchMEMMultiNode(GMXBenchMEMBase):
    descr += ' multi-node'
    executable = 'gmx_mpi mdrun'
    num_tasks = required
    num_tasks_per_node = required
    num_cpus_per_task = 1
    env_vars = {
        'OMPI_MCA_rmaps_base_mapping_policy': 'socket',
    }

    @run_after('init')
    def post_init(self):
        self.executable_opts += ['-ntomp', f'{self.num_tasks_per_node}']


@rfm.simple_test
class GMXBenchMEMSingleNodeGPU(GMXBenchMEMBase):
    descr += ' single node, multi-core, 1 or more gpus'
    executable = 'gmx mdrun'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = required
    num_gpus_per_node = required

    @run_after('init')
    def post_init(self):
        self.num_tasks_per_node = self.num_tasks
        self.executable_opts += ['-nt', f'{self.num_cpus_per_task}']
        self.env_vars = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
        }
        self.extra_resources = {
            'gpu': {'num_gpus_per_node': self.num_gpus_per_node},
        }

    @sanity_function
    def sanity_run(self):
        return sn.all([
            sn.assert_found(r'^Finished mdrun', self.logfile),
            sn.assert_found(r'^1 GPU selected for this run.', self.logfile),
        ])

