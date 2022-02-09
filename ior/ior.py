import os
import reframe as rfm
import reframe.utility.sanity as sn
import shlex
import subprocess

src_name = 'IOR'
src_version = '3.3.0'
src_dir = f'{src_name}-{src_version}'
src_file = f'{src_version}.tar.gz'
src_url = f'https://github.com/hpc/ior/archive/{src_file}'
src_base = os.path.join(os.environ['REFRAME_SOURCEPATH'], src_name[0].lower(), src_name)
src_path = os.path.join(src_base, src_file)
download_cmd = f'mkdir -p {src_base} && wget {src_url} -O {src_path}'
extract_cmd = f'mkdir {src_dir} && tar -xzvf {src_path} --strip-components 1 -C {src_dir} && cd {src_dir}'


"""
ior shared scratch storage read/write tests
options:
-o <path/to/testfile>  -- outputfile
      write to the VO scratch to make sure there is enough space.
      the current test writes 4 files (one per MPI process) of 16GB (64MB blocks * 256 segments) to disk
-t 4m  -- transferSize
-b 64m  -- blockSize
-s 256  -- segmentCount
-C  -- reorderTasks
        change task ordering for readback
        make sure that each MPI process is reading data it did not write, to avoid reading from page cache
-F  -- filePerProcess=1 one file per process instead of a single shared file. improves performance a lot
-e  -- fsync makes sure writes are done to the file system instead of to the page cache
-v  -- verbose
-D 120  -- deadlineForStonewalling in seconds before stopping write or read phase
-M 90%  --  hog memory on the node for reading
     limit the amount of memory available for page cache by allocating most of the memory on a node
     forces most of the cached pages to be evicted
     note that this is relative to the amount of memory available on the node, not the memory allocated to the job
-w  -- write file
-W  -- check read after write
-k  -- keepfile (only for the write test, since we need the files for the read test)
-r  -- read existing file
-q  -- quitOnError during file error-checking, abort on error
-v  -- verbose
(-z  -- randomOffset - access is to random, not sequential, offsets within a file) not used currently
"""


class iorTestBase(rfm.RunOnlyRegressionTest):
    "base class for ior tests"
    valid_systems = required
    valid_prog_environs = required
    time_limit = '5m'
    exe = 'ior'
    testfile = os.path.join(
        os.getenv('VSC_SCRATCH_VO_USER','doesnotexist'),
        'reframe_iortest',
        'ior_testfile',
    )
    num_tasks = required
    num_cpus_per_task = 1  # ior uses MPI
    exclusive_access = required

    @run_after('init')
    def set_executable_opts(self):
        self.executable_opts = [
            '-o', self.testfile,
            '-t', '4m',
            '-b', '64m', '-s', '256',
            '-D', '120',
            '-F', '-C', '-e', '-v', '-q',
        ]
        self.num_tasks_per_node = self.num_tasks

    @sanity_function
    def assert_run(self):
        return sn.assert_found(r'^Finished', self.stdout)

    @performance_function('MiB/s', perf_key='bandwith')
    def bandwidth(self):
        # total bandwidth: all MPI processes combined
        return sn.extractsingle(r'^Max\s+\S+\s+(\S+)\s+MiB/sec.*', self.stdout, 1, float)


@rfm.simple_test
class iorWriteTest(iorTestBase):
    descr = 'ior storage sequential write correctness and performance test'

    @run_after('init')
    def post_init(self):
        self.depends_on('iorBuildTest')
        self.executable_opts.extend(['-w', '-W', '-k'])
        self.prerun_cmds = [
            f'rm -f {self.testfile}*',
            f'mkdir -p {os.path.dirname(self.testfile)}',
        ]

    @require_deps
    def set_executable(self, iorBuildTest):
        builddir = os.path.join(iorBuildTest().stagedir, src_dir, 'src')
        self.executable = os.path.join(builddir, self.exe)


@rfm.simple_test
class iorReadTest(iorTestBase):
    descr = 'ior storage sequential read performance test'

    @run_after('init')
    def post_init(self):
        self.depends_on('iorWriteTest')
        self.depends_on('iorBuildTest')
        self.executable_opts.extend(['-r', '-M', '90%'])
        self.postrun_cmds = [f'rm -rf {os.path.dirname(self.testfile)}']

    @require_deps
    def set_executable(self, iorBuildTest):
        builddir = os.path.join(iorBuildTest().stagedir, src_dir, 'src')
        self.executable = os.path.join(builddir, self.exe)


@rfm.simple_test
class iorBuildTest(rfm.CompileOnlyRegressionTest):
    descr = 'ior build test'
    valid_systems = required
    valid_prog_environs = required
    sourcesdir = None
    prebuild_cmds = [
        download_cmd if not os.path.isfile(src_path) else '',
        extract_cmd,
        './bootstrap',
    ]
    build_locally = False
    build_system = 'Autotools'
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

