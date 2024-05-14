import glob
import json
import os
import time
import reframe as rfm
import reframe.utility.sanity as sn


os.environ["TEST_ENVAR_OUTSIDE"] = 'defined'

affinity_script = """
import json
import os
import time
affinity = list(os.sched_getaffinity(0))
task_id = os.getenv("SLURM_PROCID", "0") + "_" + os.getenv("SLURM_STEP_ID", "0")
json.dump(affinity, open(f"affinity{task_id}.json", "w"))
time.sleep(20)
"""

tempjob = """
jobid=$(sbatch --parsable --wrap=hostname --hold {} | sed 's/;.*//g')
echo job submitted: $jobid
scancel $jobid
"""


def load_affinities():
    affinities = []
    for aff in glob.glob('affinity*.json'):
        with open(aff, 'r', encoding='utf-8') as json_file:
            affinities.append(json.load(json_file))
    return affinities


class SlurmTestBase(rfm.RunOnlyRegressionTest):
    descr = "Slurm test"
    valid_systems = required
    valid_prog_environs = required
    time_limit = '10m'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1


@rfm.simple_test
class SbatchCleanEnv(SlurmTestBase):
    descr += ": sbatch starts in clean environment"
    exe = 'print(os.getenv("TEST_ENVAR_OUTSIDE") is None)'
    executable = f"python3 -c 'import os;{exe}'"

    @sanity_function
    def assert_env(self):
        return sn.all([
            sn.assert_found(r'^True$', self.stdout, self.descr),
            sn.assert_not_found(".", self.stderr, self.descr + ": no error messages")
        ])


@rfm.simple_test
class SbatchSrunCopyEnv(SlurmTestBase):
    descr += ": srun copies sbatch job environment"
    timestamp = time.time()
    prerun_cmds = [f'export TEST_ENVAR_INSIDE={timestamp}']
    exe = f'print(os.getenv("TEST_ENVAR_INSIDE") == "{timestamp}")'
    executable = f"srun python3 -c 'import os;{exe}'"

    @sanity_function
    def assert_env(self):
        return sn.all([
            sn.assert_found(r'^True$', self.stdout, self.descr),
            sn.assert_not_found(".", self.stderr, self.descr + ": no error messages")
        ])


@rfm.simple_test
class SbatchEnforceBinding(SlurmTestBase):
    descr += ": --gres-flags=enforce-binding set by default"
    executable = """
scontrol show job $SLURM_JOB_ID
sbatch --wrap=hostname --ntasks-per-node=13 --gpus-per-node=1 --partition=pascal_gpu
"""

    @sanity_function
    def assert_forcebinding(self):
        return sn.all([
            sn.assert_found(r'^\s*GresEnforceBind=Yes$', self.stdout, self.descr),
            sn.assert_found(
                r'sbatch: error: Batch job submission failed: Requested node configuration is not available',
                self.stderr,
                self.descr + ": requesting more cpus than availabe per GPU shows error"
            ),
            sn.assert_not_found(
                r"^Submitted batch job",
                self.stdout,
                self.descr + ": requesting more cpus than availabe per GPU fails"
            ),
        ])


@rfm.simple_test
class SbatchAffinity(SlurmTestBase):
    descr += ": sbatch affinity"
    num_cpus_per_task = 2
    num_tasks_per_node = 2
    num_tasks = 2
    executable = f"python3 -c '{affinity_script}'"

    @sanity_function
    def assert_affinity(self):
        affinities = load_affinities()

        return sn.all([
            sn.assert_eq(
                1,
                len(affinities),
                self.descr + ": num tasks expected: {0}, found: {1})"
            ),
            sn.assert_eq(
                self.num_cpus_per_task * self.num_tasks,
                len(affinities[0]),
                self.descr + ": num cores expected: {0}, found: {1})"
            ),
        ])


@rfm.simple_test
class SbatchSrunAffinity(SbatchAffinity):
    descr += ": srun affinity"
    # set --cpus-per-task for Slurm versions >= 22.05 < 23.11 to get the same task binding across all Slurm versions
    executable = f'srun --cpus-per-task=$SLURM_CPUS_PER_TASK {executable}'

    @sanity_function
    def assert_affinity(self):
        affinities = load_affinities()
        affinityset = {x for sublist in affinities for x in sublist}

        return sn.all([
            sn.assert_eq(
                self.num_tasks,
                len(affinities),
                self.descr + ": num tasks expected: {0}, found: {1})"
            ),
            sn.assert_eq(
                self.num_cpus_per_task,
                len(affinities[0]),
                self.descr + ": num cpus per task expected: {0}, found: {1})"
            ),
            sn.assert_eq(
                self.num_cpus_per_task * self.num_tasks,
                len(affinityset),
                self.descr + ": num unique cores expected: {0}, found: {1})"
            ),
        ])


@rfm.simple_test
class TaskFarmingParallel(SbatchSrunAffinity):
    descr += ": task farming with GNU Parallel"
    num_tasks_per_node = 1  # should work even if each task runs in a different node
    modules = ['parallel']
    affinity_script = affinity_script.replace('"', r'\"')
    # set --cpus-per-task for Slurm versions >= 22.05 < 23.11 to get the same task binding across all Slurm versions
    srun_options = '-n 1 -N 1 --exact --cpus-per-task=$SLURM_CPUS_PER_TASK'
    executable = f"seq 1 2 | parallel -N0 -j $SLURM_NTASKS \"srun {srun_options} python3 -c '{affinity_script}'\""


@rfm.simple_test
class DefaultPartitions(SlurmTestBase):
    descr += ": default list of partitions"
    tags.add('local')
    executable = """
function getpartitions {
    jobid=$(sbatch --parsable --wrap=hostname --hold $1 | sed 's/;.*//g')
    partitions=$(squeue --noheader -o "%P" -j $jobid)
    scancel $jobid
    echo $partitions
}

cat <<EOF >partitions.json
{
    "singlenode": "$(getpartitions '-n 10')",
    "multinode": "$(getpartitions '-n 2 -N 2')",
    "manycores": "$(getpartitions '-n 65')",
    "gpunode": "$(getpartitions '--gpus-per-node=1')"
}
EOF
"""

    @sanity_function
    def assert_partitions(self):
        with open('partitions.json', 'r', encoding='utf-8') as json_file:
            partitions = json.load(json_file)

        return sn.all([
            sn.assert_not_found(".", self.stderr, self.descr + ': no error messages'),
            sn.assert_eq(
                {'skylake', 'broadwell', 'skylake_mpi', 'zen4'},
                set(partitions['singlenode'].split(',')),
                self.descr + ': singlenode partitions expected: {0}, found: {1}'
            ),
            sn.assert_eq(
                {'skylake_mpi'},
                set(partitions['multinode'].split(',')),
                self.descr + ': multinode partitions expected: {0}, found: {1}'
            ),
            sn.assert_eq(
                {'skylake_mpi'},
                set(partitions['manycores'].split(',')),
                self.descr + ': manycores partitions expected: {0}, found: {1}'
            ),
            sn.assert_eq(
                {'ampere_gpu', 'pascal_gpu'},
                set(partitions['gpunode'].split(',')),
                self.descr + ': gpunode partitions expected: {0}, found: {1}'
            ),
        ])


@rfm.simple_test
class WarningMultiGPU(SlurmTestBase):
    descr += ": warning multi-GPU jobs without --ntasks-per-node"
    tags.add('local')
    executable = tempjob.format('--gpus-per-node=2')

    @sanity_function
    def assert_warning(self):
        return sn.all([
            sn.assert_found(
                r'Please use .*--ntasks-per-node.* and .*--gpus-per-node',
                self.stderr,
                self.descr
            ),
            sn.assert_found(r"^job submitted: \d+$", self.stdout, self.descr + ": job submitted successfully"),
        ])


@rfm.simple_test
class NonGPUInGPUPartition(SlurmTestBase):
    descr += ": non-GPU job in GPU partition"
    tags.add('local')
    partition = 'pascal_gpu'
    executable = tempjob.format(f'--partition={partition}')

    @run_after('init')
    def post_init(self):
        self.skip_if(os.getenv('VSC_VO', '') == 'bvo00005', self.descr + ': skipping test for bvo00005 accounts')

    @sanity_function
    def assert_forcebinding(self):
        return sn.all([
            sn.assert_found(
                rf'ERROR: GPU partition {self.partition} is not allowed for non-GPU jobs',
                self.stderr,
                self.descr + ": error message"
            ),
            sn.assert_not_found(r"^job submitted: \d+$", self.stdout, self.descr + ": no job submitted"),
        ])
