ml ReFrame/3.9.3

# append system site-packages to PYTHONPATH so reframe finds packages git and gitdb
# this is due to reframe being started with 'python3 -S'
export PYTHONPATH=$PYTHONPATH:/usr/lib64/python3.6/site-packages:/usr/lib/python3.6/site-packages

export REFRAME_SOURCEPATH='/apps/brussel/sources'

export RFM_CONFIG_FILE=$REFRAME_HOME/config/config.py

