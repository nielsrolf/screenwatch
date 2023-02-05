import os
import time
import datetime as dt
from screenwatch.configure import settings
from screenwatch.cli import get_work_logs
from glob import glob


def system(cmd):
    print(cmd)
    os.system(cmd)


def main():
    if settings.project is None:
        return
    session = len(get_work_logs())
    target_dir = os.path.join(settings.target_dir, settings.project, str(session))
    os.makedirs(target_dir, exist_ok=True)
    idx = len(glob(f"{target_dir}/*.png"))
    screen_1 = f"{target_dir}/{idx:05d}-screen1.png"
    screen_2 = f"{target_dir}/{idx:05d}-screen2.png"
    system(f"screencapture -D 1 {screen_1}")
    system(f"screencapture -D 2 {screen_2}")


if __name__ == "__main__":
    for _ in range(10):
        main()
        time.sleep(1)
