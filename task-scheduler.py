import datetime
import time
import subprocess
import pytz

def run_task():
    utc_now = datetime.datetime.utcnow() # get the current datetime object
    now = utc_now.replace(tzinfo=datetime.timezone.utc).astimezone(tz=pytz.timezone('Europe/Berlin'))

    print(f'Task Execution Time (Europe/Berlin): {utc_now.date()} {now.time()}')

    subprocess.call(["python3", "spotify-automated-top50.py"])

run_task()
while True:
    # get the current time
    now = datetime.datetime.now()

    # check if it's the start of a new hour
    if now.minute == 0 and now.second == 0:
        # run the other script
        run_task()

    # wait for one second before checking the time again
    time.sleep(1)
