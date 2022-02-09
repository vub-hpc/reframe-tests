ReFrame tests
=============


Running weekly tests for production
-----------------------------------

**Note**: performance logs are only sent to syslog/ELK when run as user `vsc10001`.

```
# login to Hydra as vsc10001
cd ~/reframe-tests
source sourceme.sh
./run_weekly.sh
```

Running tests in your account
-----------------------------

1. clone this repo in your account in Hydra
2. `source sourceme.sh`
3. copy the `run_weekly.sh` script and adapt

Location of ouput and log files
-------------------------------

* `joblobs/`: job output and job error files
* `perflogs/`: performance logs
* `stage/`, `output/`: build and run scripts, output, and error files

