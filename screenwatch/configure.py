import os
import time
import datetime as dt
import click
from pydantic import BaseModel


class Settings(BaseModel):
    # home_dir: dir of this file
    home_dir: str = os.path.dirname(os.path.abspath(__file__))
    target_dir: str = os.path.join(home_dir, "screenshots")
    interval: int = 60
    project: str = None
    task: str = None
    work_logs: str = os.path.join(home_dir, "logs.csv")


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


@click.command()
@click.argument("home_dir", default=settings.home_dir)
@click.argument("target_dir", default=settings.target_dir)
@click.argument("interval", default=settings.interval)
def set_config(
    home_dir=settings.home_dir,
    target_dir=settings.target_dir,
    interval: int = settings.interval,
):
    """Set config.json"""
    settings = Settings(
        home_dir=home_dir,
        target_dir=target_dir,
        interval=interval,
        project=settings.project,
        task=settings.task,
    )
    settings.save()
