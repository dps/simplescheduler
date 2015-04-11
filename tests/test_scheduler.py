# -*- coding: utf-8 -*-
from simplescheduler import Scheduler, Job

from datetime import timedelta
import unittest



class FakeRedis(object):

    def __init__(self):
        self._r = {}
        self._ledger = []

    def sadd(self, key, member):
        self._ledger.append('SADD %s:%s' % (key, member))
        if not self._r.has_key(key):
            self._r[key] = set()
        self._r[key].add(member)

    def get(self, key):
        value = self._r.get(key)
        self._ledger.append('GET %s (%s)' % (key, value))
        return value

    def set(self, key, value):
        self._ledger.append('SET %s=%s' % (key, value))
        self._r[key] = value

    def zadd(self, key, weight, value):
    	self._ledger.append('ZADD %s %s %s' % (key, value, weight))
    	if not self._r.has_key(key):
    		self._r[key] = []
    	self._r[key].append((weight, value))

    def zrangebyscore(self, key, start, end):
    	self._ledger.append('ZRANGEBYSCORE %s %d %d' % (key, start, end))
    	l = sorted(self._r[key], key=lambda x:x[0])
    	r = []
    	for i in l:
    		if i[0] >= start and i[0] <= end:
    			r.append(i[1])
    	return r


    def zremrangebyscore(self, key, start, end):
    	self._ledger.append('ZREMRANGEBYSCORE %s %d %d' % (key, start, end))
    	l = sorted(self._r[key], key=lambda x:x[0])
    	r = []
    	for i in l:
    		if i[0] >= start and i[0] <= end:
    			r.append(i)
    	for remove in r:
    		self._r[key].remove(remove)
    	return len(r)

    def expire(self, key, seconds):
		self._ledger.append('EXPIRE %s %d' % (key, seconds))

    def clear_ledger(self):
        self._ledger = []

    def get_ledger(self):
        return self._ledger

job_data = {}

def job1():
	print 'job1'
	job_data['job1'] = True

def job2():
	print 'job2'
	job_data['job2'] = True

def job4():
	print 'job4'
	job_data['job4'] = True

def job3():
	print 'job3'
	job_data['job3'] = True

class SchedulerUnitTests(unittest.TestCase):

	def setUp(self):
		self.fake_redis = FakeRedis()
		self.secs = 0
		self.clock_source = lambda : self.secs
		self.sleeper = lambda x : True

	def tearDown(self):
		pass

	def testRunScheduler(self):
		s = Scheduler(custom_redis=self.fake_redis,
					  clock_source=self.clock_source,
					  sleeper=self.sleeper)
		job = Job('test_scheduler.job1')
		s.schedule_now(job)
		self.secs = 1
		j2 = Job('test_scheduler.job2')
		s.schedule_now(j2)
		j3 = Job('test_scheduler.job3')
		s.schedule_in(j3, timedelta(seconds=5))
		j4 = Job('test_scheduler.job4')
		s.schedule(j4, 60 * 1e6)

		self.secs = 2
		s._run(once=True)
		assert(job_data['job1'] == True)
		assert(job_data['job2'] == True)
		assert(job_data.has_key('job3') == False)
		self.secs = 10
		s._run(once=True)
		assert(job_data['job3'] == True)
		assert(job_data.has_key('job4') == False)
		self.secs = 120
		s._run(once=True)
		assert(job_data['job4'] == True)
		
