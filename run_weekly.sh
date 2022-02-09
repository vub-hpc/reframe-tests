#!/bin/bash

# REFRAME_HOME is the directory of the current script
export REFRAME_HOME=$(dirname $(realpath -s "$0"))
echo REFRAME_HOME=$REFRAME_HOME

source $REFRAME_HOME/sourceme.sh

# use 1 or 0
TEST_IVYBRIDGE=1
TEST_BROADWELL=1
TEST_SKYLAKE=1
TEST_AMPERE=1
TEST_PASCAL=1

# exclusive_access (Slurm option --exclusive)
EXCLUSIVE_SN=true
EXCLUSIVE_MN=false
EXCLUSIVE_IO=true

# systems
IVYBRIDGE_SN='hydra:ivybridge-sn'
IVYBRIDGE_MPI='hydra:ivybridge-mpi'
BROADWELL_SN='hydra:broadwell-sn'
BROADWELL_MPI='hydra:broadwell-mpi'
PASCAL_SN='hydra:broadwell-pascal-sn'
SKYLAKE_MN_MPI_IB='hydra:skylake-mn-mpi-ib'
SKYLAKE_MN_MPI_ETH='hydra:skylake-mn-mpi-eth'
SKYLAKE_SN='hydra:skylake-sn'
SKYLAKE_SN_MPI='hydra:skylake-sn-mpi'
AMPERE_SN='hydra:zen2-ampere-sn'
LOCAL_SN='hydra:local-sn'  # for running locally (no job)

if [ $TEST_IVYBRIDGE -eq 0 ];then
    IVYBRIDGE_SN=''
    IVYBRIDGE_MPI=''
fi

if [ $TEST_BROADWELL -eq 0 ];then
    BROADWELL_SN=''
    BROADWELL_MPI=''
fi

if [ $TEST_SKYLAKE -eq 0 ];then
    SKYLAKE_MN_MPI_IB=''
    SKYLAKE_MN_MPI_ETH=''
    SKYLAKE_SN=''
    SKYLAKE_SN_MPI=''
fi

if [ $TEST_PASCAL -eq 0 ];then
    PASCAL_SN=''
fi

if [ $TEST_AMPERE -eq 0 ];then
    AMPERE_SN=''
fi

# first run tests that run sequentially (multi-node and shared storage tests):
# use multi-node ReFrame 'partitions' to ensure that only one job can run in a partition (see 'max_jobs' in configuration file)
# ior shared storage
cd $REFRAME_HOME/ior/ && reframe --verbose --run \
    --checkpath ior.py \
    --setvar iorBuildTest.num_cpus_per_task=4 \
    --setvar iorWriteTest.num_tasks=4 \
    --setvar iorReadTest.num_tasks=4 \
    --setvar iorWriteTest.exclusive_access=$EXCLUSIVE_IO \
    --setvar iorReadTest.exclusive_access=$EXCLUSIVE_IO \
    --setvar valid_systems=$SKYLAKE_MN_MPI_IB \
    --setvar valid_prog_environs=foss-2021a

cd $REFRAME_HOME/ior/ && reframe --verbose --run \
    --checkpath ior.py \
    --setvar iorBuildTest.num_cpus_per_task=4 \
    --setvar iorWriteTest.num_tasks=4 \
    --setvar iorReadTest.num_tasks=4 \
    --setvar iorWriteTest.exclusive_access=$EXCLUSIVE_IO \
    --setvar iorReadTest.exclusive_access=$EXCLUSIVE_IO \
    --setvar valid_systems=$SKYLAKE_MN_MPI_ETH \
    --setvar valid_prog_environs=foss-2021a

# osu multi-node
cd $REFRAME_HOME/osu/ && reframe --verbose --run \
    --exec-policy serial \
    --checkpath osu.py \
    --setvar OSULatencyTest.num_tasks=2 \
    --setvar OSUBandwidthTest.num_tasks=2 \
    --setvar OSUBuildTest.num_cpus_per_task=4 \
    --setvar OSULatencyTest.exclusive_access=$EXCLUSIVE_MN \
    --setvar OSUBandwidthTest.exclusive_access=$EXCLUSIVE_MN \
    --setvar valid_systems=$SKYLAKE_MN_MPI_IB,$IVYBRIDGE_MPI \
    --setvar valid_prog_environs=foss-2021a,intel-2021a \
    --tag prod_small

# gromacs multi-node
cd $REFRAME_HOME/gromacs_bench/ && reframe --verbose --run \
    --checkpath gromacs.py \
    --setvar modules='GROMACS/2021.3-foss-2021a' \
    --setvar num_tasks=4 \
    --setvar num_tasks_per_node=1 \
    --setvar exclusive_access=$EXCLUSIVE_MN \
    --setvar valid_systems=$SKYLAKE_MN_MPI_IB,$IVYBRIDGE_MPI \
    --name GMXBenchMEMMN

# cp2k multi-node
cd $REFRAME_HOME/cp2k_tests/ && reframe --verbose --run \
    --checkpath cp2k.py \
    --setvar modules='CP2K/7.1-intel-2020a' \
    --setvar num_tasks=4 \
    --setvar num_tasks_per_node=1 \
    --setvar exclusive_access=$EXCLUSIVE_MN \
    --setvar valid_systems=$SKYLAKE_MN_MPI_IB,$IVYBRIDGE_MPI \
    --name CP2KTestMN

# next run single-node tests with Slurm --exclusive flag so all tests can run in parallel
# blas
cd $REFRAME_HOME/blas-tester/ && reframe --verbose --run \
    --checkpath blas.py \
    --setvar num_cpus_per_task=4 \
    --setvar BLASTest.exclusive_access=$EXCLUSIVE_SN \
    --setvar valid_systems=$SKYLAKE_SN,$BROADWELL_SN,$IVYBRIDGE_SN \
    --setvar valid_prog_environs=foss-2021a,intel-2021a \
    &

# gromacs single-node
cd $REFRAME_HOME/gromacs_bench/ && reframe --verbose --run \
    --checkpath gromacs.py \
    --setvar modules='GROMACS/2021.3-foss-2021a' \
    --setvar num_cpus_per_task=4 \
    --setvar exclusive_access=$EXCLUSIVE_SN \
    --setvar valid_systems=$SKYLAKE_SN,$BROADWELL_SN,$IVYBRIDGE_SN \
    --name GMXBenchMEMMC \
    &

# gromacs single-node GPU
cd $REFRAME_HOME/gromacs_bench/ && reframe --verbose --run \
    --checkpath gromacs.py \
    --setvar modules='GROMACS/2021.3-foss-2021a-CUDA-11.3.1' \
    --setvar num_cpus_per_task=4 \
    --setvar num_gpus_per_node=1 \
    --setvar exclusive_access=$EXCLUSIVE_SN \
    --setvar valid_systems=$PASCAL_SN,$AMPERE_SN \
    --name GMXBenchMEMGPU \
    &

# cp2k single-node
cd $REFRAME_HOME/cp2k_tests/ && reframe --verbose --run \
    --checkpath cp2k.py \
    --setvar modules='CP2K/7.1-intel-2020a' \
    --setvar num_tasks=4 \
    --setvar exclusive_access=$EXCLUSIVE_SN \
    --setvar valid_systems=$SKYLAKE_SN_MPI,$BROADWELL_MPI,$IVYBRIDGE_MPI \
    --name CP2KTestMC \
    &

wait

