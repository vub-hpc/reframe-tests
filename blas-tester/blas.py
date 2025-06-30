import os

import reframe as rfm
import reframe.utility.sanity as sn


src_name = 'BLAS-Tester'
src_version = '20160411'
src_dir = f'{src_name}-{src_version}'
src_url = 'https://github.com/xianyi/BLAS-Tester/archive/8e1f624.tar.gz'
src_path = os.path.join(os.environ['REFRAME_SOURCEPATH'], src_name[0].lower(), src_name, f'{src_dir}.tar.gz')

download_cmd = f'wget {src_url} -O {src_path}'
extract_cmd = f'mkdir {src_dir} && tar -xzvf {src_path} --strip-components 1 -C {src_dir} && cd {src_dir}'
patch_cmd = "sed -i -e 's/-openmp/-qopenmp/g' Makefile.system"


@rfm.simple_test
class BLASTest(rfm.RunOnlyRegressionTest):
    "BLAS correctness and performance tests"
    exe = parameter(['xcl3', 'xdl3', 'xsl3', 'xzl3'])
    valid_systems = required
    valid_prog_environs = required
    time_limit = '10m'
    test_index = '9'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = required
    exclusive_access = required

    @run_after('init')
    def post_init(self):
        self.descr = f'BLAS-Tester {self.exe} test'
        self.depends_on('BLASBuildTest')
        self.env_vars = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
        }

    @require_deps
    def set_executable(self, BLASBuildTest):
        self.executable = os.path.join(BLASBuildTest().stagedir, src_dir, 'bin', f'{self.exe}blastst')

    @sanity_function
    def assert_run(self):
        return sn.assert_found(r'^10 tests run, 10 passed', self.stdout)

    @performance_function('MFLOPS', perf_key='speed')
    def speed(self):
        return sn.extractsingle(rf'^\s+{self.test_index}.*\s+(\S+)\s+\S+\s+PASS', self.stdout, 1, float)


@rfm.simple_test
class BLASBuildTest(rfm.CompileOnlyRegressionTest):
    descr = 'BLAS-Tester build test'
    valid_systems = required
    valid_prog_environs = required
    build_locally = False
    sourcesdir = None
    prebuild_cmds = [
        download_cmd if not os.path.isfile(src_path) else '',
        extract_cmd,
        patch_cmd,
    ]
    build_system = 'Make'
    num_cpus_per_task = required

    @run_after('setup')
    def set_cpus_per_task(self):
        self.build_job.num_cpus_per_task = self.num_cpus_per_task
        self.build_job.num_tasks = 1
        self.build_job.num_tasks_per_node = 1

    @run_before('compile')
    def set_build_system_options(self):
        self.build_system.options = [
            'CODEBITS=-Wno-implicit-function-declaration',
            f'NUMTHREADS={self.num_cpus_per_task}',
            'USE_OPENMP=1',
            'L2SIZE=$(getconf LEVEL2_CACHE_SIZE)',
        ]

    @run_before('compile')
    def set_max_concurrency(self):
        self.build_system.max_concurrency = self.num_cpus_per_task

    @run_before('compile')
    def setflags(self):
        flags_openblas = ['TEST_BLAS=$EBROOTOPENBLAS/lib/libopenblas.so']
        flags_mkl = [
            'TEST_BLAS=$MKLROOT/lib/intel64/libmkl.so',
            'F_INTERFACE_INTEL=1',
            'LIBS="-liomp5 -lpthread"',
        ]

        if self.current_environ.name.startswith('foss'):
            self.build_system.options.extend(flags_openblas)
        elif self.current_environ.name.startswith('intel'):
            self.build_system.options.extend(flags_mkl)

    @sanity_function
    def validate_build(self):
        return sn.assert_not_found('error', self.stderr)

