ml ReFrame/4.7.4-GCCcore-13.3.0 GitPython/3.1.43-GCCcore-13.3.0

export REFRAME_HOME=$PWD
echo REFRAME_HOME=$REFRAME_HOME

export REFRAME_SOURCEPATH='/apps/brussel/sources'

export RFM_CONFIG_FILES=$REFRAME_HOME/config/config.py
export RFM_PREFIX=$VSC_SCRATCH_VO_USER/hpc-reframe-tests
export RFM_OUTPUT_DIR=$RFM_PREFIX
export RFM_PERFLOG_DIR=$RFM_PREFIX/perflogs
export RFM_SAVE_LOG_FILES=true
export RFM_VERBOSE

mkdir -p $RFM_PREFIX/logs
