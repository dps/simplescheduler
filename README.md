# simplescheduler
[![Build status](https://travis-ci.org/dps/simplescheduler.svg?branch=master)](https://secure.travis-ci.org/dps/simplescheduler)

A simple task scheduler using redis for python.

I have tried some of the more popular task schedulers for python, including rq + rqscheduler and apscheduler but had problems making them work reliably in production.

Simple scheduler is simple.  It's dumb.  But it works, and it's so simple that if it does go wrong, you can probably debug it yourself.

## Getting started

First, run a Redis server:

```console
$ redis-server
```

To run jobs later, just define your blocking function:

```python
in myfile.py

def job(message):
    print 'job done: %s' % message
```

Then, create a job, scheduler instance and schedule the job:

```python
from datetime import timedelta
from simplescheduler import Job, Scheduler

j = Job('myfile.job', ['example parameter'])
s = Scheduler()
s.schedule_in(j, timedelta(hours=1))
```

### The worker

To start executing scheduled function calls in the background, set environment variables corresponding to your redis instance and start a worker from your project's directory:

```console
$ export REDIS_HOST=localhost
$ export REDIS_PORT=6397
$ export REDIS_DB=0
$ export REDIS_KEY=

$ ss
Start ss:sched:1428788600124490
```


## Installation

Simply use the following command to install the latest released version:

    pip install simplescheduler

