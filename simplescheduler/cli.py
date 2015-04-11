# -*- coding: utf-8 -*-
import argparse
from .scheduler import Job, Scheduler
from .version import VERSION
__version__ = VERSION

parser = argparse.ArgumentParser(description='SimpleScheduler')
parser.add_argument('--interval',
                    type=int,
                    default=5,
                    help='Interval in seconds between scheduler polls.')
parser.add_argument('--verbose',
                    type=bool,
                    default=False,
                    help='Be more verbose.')
parser.add_argument('--keepalive',
                    type=bool,
                    default=False,
                    help='Run a keepalive task.')

def main():
    """ SimpleScheduler
    redis parameters will be read from environment variables:
    REDIS_HOST, REDIS_PORT,REDIS_DB,REDIS_KEY (password)
    """
    args = parser.parse_args()

    scheduler = Scheduler()

    print 'Start %s' % scheduler.scheduler_id
    scheduler.interval = args.interval
    if args.keepalive:
        scheduler.run(once=True)
        keepalive = Job('simplescheduler.keepalive',
                        args=[0,
                              scheduler.get_running_scheduler_id(),
                              args.interval * 2])
        scheduler.schedule(keepalive, long(time.time() * 1000000))
    scheduler.run()