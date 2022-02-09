import os
import reframe as rfm
import reframe.utility.sanity as sn

src_name = 'c-ray'
src_version = '1.1'
src_dir = f'{src_name}-{src_version}'
src_url = f'https://www.phoronix.net/downloads/phoronix-test-suite/benchmark-files/{src_dir}.tar.gz'
src_path = os.path.join(os.environ['REFRAME_SOURCEPATH'], src_name[0].lower(), src_name, f'{src_dir}.tar.gz')
download_cmd = f'wget {src_url} -O {src_path}'
extract_cmd = f'mkdir {src_dir} && tar -xzvf {src_path} --strip-components 1 -C {src_dir} && cd {src_dir}'


class c_rayTestBase(rfm.RunOnlyRegressionTest):
    "base class for c-ray test"
    descr = 'c-ray ray tracing test (FPU performance)'
    time_limit = '15m'
    testfile = 'sphfract'
    exe = 'c-ray-mt'
    valid_systems = required
    valid_prog_environs = required
    num_tasks = 1
    num_tasks_per_node = 1
    exclusive_access = required

    @run_after('init')
    def post_init(self):
        self.depends_on('c_rayBuildTest')

    @sanity_function
    def assert_run(self):
        return sn.assert_found(r'^Rendering took:', self.stderr)

    @performance_function('s', perf_key='time')
    def time(self):
        return sn.extractsingle(rf'^Rendering took: (\S+) seconds', self.stderr, 1, int)


@rfm.simple_test
class c_rayTestSC(c_rayTestBase):
    time_limit = '15m'
    num_cpus_per_task = 1

    @require_deps
    def set_executable(self, c_rayBuildTest):
        builddir = os.path.join(c_rayBuildTest().stagedir, src_dir)
        resolution = '5000x2500'
        rays = '4'
        self.executable = os.path.join(builddir, self.exe)
        self.executable_opts = [
            '-i', os.path.join(builddir, self.testfile),
            '-s', resolution,
            '-r', rays,
            '-t', f'{self.num_cpus_per_task}',
            '>/dev/null',
        ]


@rfm.simple_test
class c_rayTestMC(c_rayTestBase):
    time_limit = '15m'
    num_cpus_per_task = required

    @run_after('init')
    def set_variables(self):
        self.variables = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
            'OMP_PLACES': 'sockets',
        }

    @require_deps
    def set_executable(self, c_rayBuildTest):
        builddir = os.path.join(c_rayBuildTest().stagedir, src_dir)
        resolution = '7000x3500'
        rays = '8'
        self.executable = os.path.join(builddir, self.exe)
        self.executable_opts = [
            '-i', os.path.join(builddir, self.testfile),
            '-s', resolution,
            '-r', rays,
            '-t', f'{self.num_cpus_per_task}',
            '>/dev/null',
        ]


@rfm.simple_test
class c_rayBuildTest(rfm.CompileOnlyRegressionTest):
    descr = 'c-ray build test'
    valid_systems = required
    valid_prog_environs = required
    sourcesdir = None
    prebuild_cmds = [
        download_cmd if not os.path.isfile(src_path) else '',
        extract_cmd,
        'make clean',
    ]
    build_locally = False
    build_system = 'Make'
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


