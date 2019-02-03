from apscheduler.schedulers.blocking import BlockingScheduler
import camera
from log import log

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=30)
def timed_job():
    log.info('running scheduled interval job to capture image')
    camera.capture_single_image()

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
