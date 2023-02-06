import datetime as dt
import os
from glob import glob
import subprocess
import time

from screenwatch.configure import settings, get_work_logs


def system(cmd):
    """Run a command in the shell, surpress outputs"""
    with open(os.devnull, "w") as f:
        subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)


def main():
    if settings.project is None:
        return
    session = len(get_work_logs())
    target_dir = os.path.join(settings.target_dir, settings.project, str(session))
    os.makedirs(target_dir, exist_ok=True)
    idx = len(glob(f"{target_dir}/*.png"))
    screen_1 = f"{target_dir}/{idx:05d}-screen1.png"
    screen_2 = f"{target_dir}/{idx:05d}-screen2.png"
    system(f"/usr/sbin/screencapture -D 1 {screen_1}")
    system(f"/usr/sbin/screencapture -D 2 {screen_2}")
    time.sleep(settings.interval * 60)
    subprocess.Popen([settings.python, __file__])


if __name__ == "__main__":
    main()
