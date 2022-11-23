ReFrame tests
=============


Running weekly tests for production
-----------------------------------

**Note**: performance logs are only sent to syslog/ELK when run as user `vsc10001`.

```
# login to Hydra as vsc10001
cd ~/reframe-tests
./run_weekly.sh
```

Running tests in your account
-----------------------------

```
git clone git@ssh.dev.azure.com:v3/VUB-ICT/Directie%20ICT/HPC_reframe-tests
cd HPC_Reframe-tests
./run.sh <options>
```

Examples
--------

```
# all Lmod tests as jobs in compute nodes
./run.sh -c lmod
# Lmod test LmodTestJavaMemory in the local node
./run.sh -c lmod -n LmodTestJavaMemory --system local
# OSU tests compiled with foss/2022a toolchain
./run.sh -c osu --valid_prog_environs foss-2022a
# OSU tests in ReFrame partition skylake-mn-mpi-ib
./run.sh -c osu --partitions skylake-mn-mpi-ib
# GROMACS GPU test in ReFrame partition zen2-ampere-sn-gpu
./run.sh -c gromacs_bench --partition zen2-ampere-sn-gpu -n GMXBenchMEMSingleNodeGPU
```

Location of ouput and log files
-------------------------------

All output is written to `VSC_SCRATCH_VO_USER/hpc-reframe-tests/`

* `logs/` ReFrame log files
* `perflogs/`: performance logs
* `stage/`: build and run scripts, (job) output, and (job) error files

