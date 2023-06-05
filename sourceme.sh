ml ReFrame/4.2.0

export REFRAME_HOME=$PWD
echo REFRAME_HOME=$REFRAME_HOME

# append system site-packages to PYTHONPATH so reframe finds packages git and gitdb
# this is due to reframe being started with 'python3 -S'
export PYTHONPATH=$PYTHONPATH:/usr/lib64/python3.6/site-packages:/usr/lib/python3.6/site-packages

export REFRAME_SOURCEPATH='/apps/brussel/sources'

export RFM_CONFIG_FILES=$REFRAME_HOME/config/config.py
export RFM_PREFIX=$VSC_SCRATCH_VO_USER/hpc-reframe-tests
export RFM_OUTPUT_DIR=$RFM_PREFIX
export RFM_PERFLOG_DIR=$RFM_PREFIX/perflogs
export RFM_SAVE_LOG_FILES=true
export RFM_VERBOSE

mkdir -p $RFM_PREFIX/logs
