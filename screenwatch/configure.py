import os

import pandas as pd
from pydantic import BaseModel


class Settings(BaseModel):
    # home_dir: dir of this file
    home_dir: str = os.path.dirname(os.path.abspath(__file__))
    target_dir: str = os.path.join(home_dir, "screenshots")
    interval: int = 60
    project: str = None
    task: str = None
    work_logs: str = os.path.join(home_dir, "logs.csv")
    python: str = "python"

    def save(self):
        with open(os.path.join(self.home_dir, "config.json"), "w") as f:
            f.write(self.json())


# read settings from config.json
try:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    ) as f:
        settings = Settings.parse_raw(f.read())
except FileNotFoundError:
    settings = Settings()


os.makedirs(settings.target_dir, exist_ok=True)


def get_work_logs():
    try:
        df = pd.read_csv(settings.work_logs)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["project", "task", "start", "end"])
    return df