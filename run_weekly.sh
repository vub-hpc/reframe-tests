#!/bin/bash

cd $(dirname "$0")

# shared storage test
./run.sh -c ior --partitions skylake-mn-mpi-ib
./run.sh -c ior --partitions skylake-mn-mpi-eth

# multi-node tests
./run.sh -c osu
./run.sh -c gromacs_bench -n GMXBenchMEMMultiNode
./run.sh -c cp2k_tests -n CP2KTestMultiNode

# single-node tests
./run.sh -c blas-tester
./run.sh -c gromacs_bench -n GMXBenchMEMSingleNode
./run.sh -c gromacs_bench -n GMXBenchMEMSingleNodeGPU
./run.sh -c cp2k_tests -n CP2KTestSingleNode

