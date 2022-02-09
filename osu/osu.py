import os

import reframe as rfm
import reframe.utility.sanity as sn

src_name = 'osu-micro-benchmarks'
src_version = '5.6.2'
src_dir = f'{src_name}-{src_version}'
src_url = 'https://mvapich.cse.ohio-state.edu/download/mvapich/{src_dir}.tar.gz'
src_path = os.path.join(os.environ['REFRAME_SOURCEPATH'], src_name[0].lower(), src_name, f'{src_dir}.tar.gz')

download_cmd = f'wget {src_url} -O {src_path}'
extract_cmd = f'mkdir {src_dir} && tar -xzvf {src_path} --strip-components 1 -C {src_dir} && cd {src_dir}'


# executable options:
# -x: nb of warmup iterations
# -i nb of timing iterations
# -m message size (runs with increasing message size up to this value)


class OSUTestBase(rfm.RunOnlyRegressionTest):
    '''Base class of OSU benchmarks runtime tests'''
    valid_systems = required
    valid_prog_environs = required
    num_tasks = required
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    time_limit = '15m'
    exclusive_access = required

    # packet sizes
    size_small = str(2 << 10)
    size_big = str(64 << 10)

    @run_after('init')
    def post_init(self):
        self.depends_on('OSUBuildTest')

    @sanity_function
    def assert_run(self):
        return sn.assert_found(r'^8', self.stdout)

class OSUTestLatencyBase(OSUTestBase):
    "base class for OSU benchmarks that measure latency"
    @performance_function('us', perf_key='latency_small')
    def latency_small(self):
        return sn.extractsingle(rf'^{self.size_small}\s+(\S+)', self.stdout, 1, float)

    @performance_function('us', perf_key='latency_big')
    def latency_big(self):
        return sn.extractsingle(rf'^{self.size_big}\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class OSULatencyTest(OSUTestLatencyBase):
    descr = 'OSU latency test'
    tags = {'prod_small'}

    @require_deps
    def set_executable(self, OSUBuildTest):
        self.executable = os.path.join(OSUBuildTest().stagedir, src_dir, 'mpi', 'one-sided', 'osu_get_latency')
        self.executable_opts = ['-x', '100', '-i', '10000']


@rfm.simple_test
class OSUBandwidthTest(OSUTestBase):
    descr = 'OSU bandwidth test'
    tags = {'prod_small'}

    @performance_function('MB/s', perf_key='bandwidth_small')
    def bandwidth_small(self):
        return sn.extractsingle(rf'^{self.size_small}\s+(\S+)', self.stdout, 1, float)

    @performance_function('MB/s', perf_key='bandwidth_big')
    def bandwidth_big(self):
        return sn.extractsingle(rf'^{self.size_big}\s+(\S+)', self.stdout, 1, float)

    @require_deps
    def set_executable(self, OSUBuildTest):
        self.executable = os.path.join(OSUBuildTest().stagedir, src_dir, 'mpi', 'one-sided', 'osu_get_bw')
        self.executable_opts = ['-x', '100', '-i', '5000', '-m', self.size_big]


@rfm.simple_test
class OSUAlltoallTest(OSUTestLatencyBase):
    descr = 'OSU Alltoall test'
    tags = {'prod_big'}

    @require_deps
    def set_executable(self, OSUBuildTest):
        self.executable = os.path.join(OSUBuildTest().stagedir, src_dir, 'mpi', 'collective', 'osu_alltoall')
        self.executable_opts = ['-x', '1000', '-i', '20000']

@rfm.simple_test
class OSUAllreduceTest(OSUTestLatencyBase):
    descr = 'OSU Allreduce test'
    tags = {'prod_big'}

    @require_deps
    def set_executable(self, OSUBuildTest):
        self.executable = os.path.join(OSUBuildTest().stagedir, src_dir, 'mpi', 'collective', 'osu_allreduce')
        self.executable_opts = ['-x', '1000', '-i', '20000']

@rfm.simple_test
class OSUBuildTest(rfm.CompileOnlyRegressionTest):
    descr = 'OSU benchmarks build test'
    valid_systems = required
    valid_prog_environs = required
    sourcesdir = None
    prebuild_cmds = [
        download_cmd if not os.path.isfile(src_path) else '',
        extract_cmd,
    ]
    build_system = 'Autotools'
    tags = {'prod_small', 'prod_big'}
    build_locally = False
    num_cpus_per_task = required

    @run_after('setup')
    def set_resources(self):
        self.build_job.num_tasks = 1
        self.build_job.num_tasks_per_node = 1
        self.build_job.num_cpus_per_task = self.num_cpus_per_task

    @run_before('compile')
    def set_max_concurrency(self):
        self.build_system.max_concurrency = self.num_cpus_per_task

    @sanity_function
    def validate_build(self):
        return sn.assert_not_found('error', self.stderr)

