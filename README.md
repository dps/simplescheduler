# simplescheduler
A simple task scheduler using redis for python 

## Getting started

First, run a Redis server:

```console
$ redis-server
```

To run jobs later, you don't have to do anything special, just define
your typically lengthy or blocking function:

```python myfile.py

def job(message):
    print 'job done: %s' % message
```

Then, create a job, scheduler instance and schedule the job:

```python
from datetime import timedelta
from simplescheduler import Job, Scheduler

j = Job('myfile.job', 'foo')
s = Scheduler()
s.schedule_in(j, timedelta(hours=1))
```

### The worker

To start executing scheduled function calls in the background, set environment variables corresponding to your redis instance and start a worker from your project's directory:

```console
$ export REDIS_HOST=localhost
$ export REDIS_PORT=localhost
$ export REDIS_DB=0
$ export REDIS_KEY=

$ ss
Start ss:sched:1428788600124490
```


## Installation

Simply use the following command to install the latest released version:

    pip install simplescheduler

