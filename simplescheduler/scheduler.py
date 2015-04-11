# -*- coding: utf-8 -*-
import importlib
import redis
import time
import os
import pickle
import traceback

class Job(object):

    def __init__(self, name, args=[], kwargs={}):
        self.name = name
        self.args = args
        self.kwargs = kwargs


class Scheduler(object):

    def __init__(self, custom_redis=None,
                 clock_source=None,
                 sleeper=None,
                 interval=5,
                 verbose=False):
        self.scheduler_id = 'ss:sched:' + str(int(time.time() * 1000000))
        self.interval = interval
        self.clock_source = clock_source
        self.sleeper = sleeper
        self.verbose = verbose
        if custom_redis:
            self._redis = custom_redis
        else:
            self._redis = redis.StrictRedis(
                            host=os.environ['REDIS_HOST'],
                            port=int(os.environ['REDIS_PORT']),
                            db=int(os.environ['REDIS_DB']),
                            password=os.environ['REDIS_KEY'])

    def _now(self):
        if self.clock_source:
            return self.clock_source()
        else:
            return time.time()

    def _sleep(self, seconds):
        if self.sleeper:
            self.sleeper(seconds)
        else:
            time.sleep(seconds)

    def _get_newly_runnable_jobs(self):
        now = long(self._now() * 1000000)
        last = self._redis.get(self.scheduler_id + '_lastpoll')
        if not last:
            last = 0
        last = long(last)
        self._redis.set(self.scheduler_id + '_lastpoll', str(now))
        self._redis.expire(self.scheduler_id + '_lastpoll', self.interval * 10)

        jobs = self._redis.zrangebyscore('ss:scheduled', last, now)
        rcount = self._redis.zremrangebyscore('ss:scheduled', last, now)
        if (rcount != len(jobs)):
            print "******* CRITICAL: %d != jobs:[%d]" % (rcount, len(jobs))
        result = []
        for job in jobs:
            result.append(pickle.loads(job))
        return result

    def schedule(self, job, when):
        """ Schedule job to run at when nanoseconds since the UNIX epoch."""
        pjob = pickle.dumps(job)
        self._redis.zadd('ss:scheduled', when, pjob)

    def schedule_in(self, job, timedelta):
        """ Schedule job to run at datetime.timedelta from now."""
        now = long(self._now() * 1e6)
        when = now + timedelta.total_seconds() * 1e6
        self.schedule(job, when)

    def schedule_now(self, job):
        """ Schedule job to run as soon as possible."""
        now = long(self._now() * 1e6)
        self.schedule(job, now)


    def get_running_scheduler_id(self):
        return self._redis.get('ss:running_scheduler')

    def _ensure_only_one_scheduler(self):
        check = True
        while check:
            redis_id = self._redis.get('ss:running_scheduler')
            if redis_id and redis_id != self.scheduler_id:
                print '******* Another scheduler may be running (%s != %s)' % (
                    redis_id, self.scheduler_id)
                self._sleep(self.interval)
            else:
                check = False
        self._redis.set('ss:running_scheduler', self.scheduler_id)
        self._redis.expire('ss:running_scheduler', self.interval * 2)

    def _run(self, once=False):
        if self.verbose:
            print 'Scheduler %s running.' % self.scheduler_id

        while(True):
            self._ensure_only_one_scheduler()
            jobs = self._get_newly_runnable_jobs()
            for job in jobs:
                if self.verbose:
                    print "+running %s " % job.name
                result = None
                try:
                    module_name, attribute = job.name.rsplit('.', 1)
                    module = importlib.import_module(module_name)
                    func = getattr(module, attribute)
                    result = func(*job.args, **job.kwargs)
                except Exception, e:
                    print "******* Exception thrown"
                    print e
                if self.verbose:
                    print "-running %s" % (job.name)
            if once:
                return
            else:
                self._sleep(self.interval)
