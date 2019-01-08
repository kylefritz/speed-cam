from apscheduler.schedulers.blocking import BlockingScheduler
import camera

sched = BlockingScheduler()

@sched.scheduled_job('save_occasional_image', minutes=30)
def timed_job():
    camera.capture_single_image()

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
