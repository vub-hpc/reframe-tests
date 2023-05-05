import os
import reframe as rfm
import reframe.utility.sanity as sn


os.environ["TEST_ENVAR_OUTSIDE"] = 'defined'

affinity_script = """
import os
affinity = os.sched_getaffinity(0)
print("num_cores: " + str(len(affinity)))
for aff in affinity:
    print("affinity: " + str(aff))"""


class SlurmTestBase(rfm.RunOnlyRegressionTest):
    descr = "Slurm test: "
    valid_systems = required
    valid_prog_environs = required
    time_limit = '10m'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1


@rfm.simple_test
class SbatchCleanEnvTest(rfm.RunOnlyRegressionTest):
    descr += "sbatch starts in a clean environment"
    exe = 'print(os.getenv("TEST_ENVAR_OUTSIDE") is None)'
    executable = f"python3 -c 'import os;{exe}'"

    @sanity_function
    def assert_env(self):
        return sn.assert_found(r'^True$', self.stdout, self.descr)


@rfm.simple_test
class SbatchSrunCopyEnvTest(rfm.RunOnlyRegressionTest):
    descr += "srun copies the sbatch job environment"
    prerun_cmds = ['export TEST_ENVAR_INSIDE=defined']
    exe = 'print(os.environ["TEST_ENVAR_INSIDE"] == "defined")'
    executable = f"srun python3 -c 'import os;{exe}'"

    @sanity_function
    def assert_env(self):
        return sn.assert_found(r'^True$', self.stdout, self.descr)


@rfm.simple_test
class SbatchEnforceBindingTest(rfm.RunOnlyRegressionTest):
    descr += "--gres-flags=enforce-binding is set"
    executable = "scontrol show job $SLURM_JOB_ID"

    @sanity_function
    def assert_forcebinding(self):
        return sn.assert_found(r'^\s*GresEnforceBind=Yes$', self.stdout, self.descr)


@rfm.simple_test
class SbatchAffinity(rfm.RunOnlyRegressionTest):
    descr += "sbatch affinity: "
    num_cpus_per_task = 2
    num_tasks_per_node = 2
    num_tasks = 2
    executable = f"python3 -c '{affinity_script}'"

    @sanity_function
    def assert_affinity(self):
        num_tasks = sn.len(sn.findall(rf'^num_cores: ({self.num_cpus_per_task * self.num_tasks})$', self.stdout))
        affinities = sn.extractall(r'^affinity: (.*)$', self.stdout)

        return sn.assert_eq(
            1,
            num_tasks,
            self.descr + "num tasks expected: {0}, found: {1})"
        ),


@rfm.simple_test
class SbatchSrunAffinity(SbatchAffinity):
    descr += "srun affinity: "
    executable = 'srun ' + executable

    @sanity_function
    def assert_affinity(self):
        num_tasks = sn.len(sn.findall(rf'^num_cores: ({self.num_cpus_per_task})$', self.stdout))
        affinities = sn.extractall(r'^affinity: (.*)$', self.stdout)

        return sn.all([
            sn.assert_eq(
                self.num_tasks,
                num_tasks,
                self.descr + "num tasks expected: {0}, found: {1})"
            ),
            sn.assert_eq(
                self.num_tasks * self.num_cpus_per_task,
                sn.count_uniq(affinities),
                "num unique cores expected: {0}, found: {1})"
            ),
        ])


@rfm.simple_test
class TaskFarmingParallel(SbatchSrunAffinity):
    descr += "task farming with GNU Parallel: "
    modules = ['parallel']
    affinity_script = affinity_script.replace('"', r'\"')
    executable = f"seq 1 2 | parallel -N0 -j $SLURM_NTASKS \"srun -n 1 -N 1 --exact python3 -c '{affinity_script}'\""
