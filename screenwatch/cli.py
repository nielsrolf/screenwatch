import click
from screenwatch.configure import settings, Settings
import pandas as pd
import os


def get_work_logs():
    try:
        df = pd.read_csv(settings.work_logs)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["project", "task", "start", "end"])
    return df


@click.command("start")
@click.argument("project")
@click.argument("task", required=False)
def startwork(project: str, task: str = None):
    """Start a work session"""
    _stopwork()
    df = get_work_logs()
    df = df.append(
        {
            "project": project,
            "task": task,
            "start": pd.Timestamp.now(),
        }, ignore_index=True
    )
    df.to_csv(settings.work_logs, index=False)
    settings.project = project
    settings.task = task
    settings.save()
    click.echo(f"Started work on {project} {task}")


@click.command("stop")
def stopwork():
    _stopwork()


def create_video():
    """Create a video from the screenshots"""
    df = get_work_logs()
    session = len(df)
    target_dir = os.path.join(settings.target_dir, settings.project, str(session))
    # use ffmpeg to create one video per screen
    for screen in [1, 2]:
        cmd = f"ffmpeg -framerate 1 -pattern_type glob -i '{target_dir}/*-screen{screen}.png' -c:v libx264 -r 30 -pix_fmt yuv420p {target_dir}/screen{screen}.mp4"
        print(cmd)
        os.system(cmd)


def _stopwork():
    """Stop a work session"""
    df = get_work_logs()
    # if the last entry is not finished, finish it
    if pd.isnull(df.iloc[-1]["end"]):
        df.at[df.index[-1], "end"] = pd.Timestamp.now()
        df.to_csv(settings.work_logs, index=False)
        create_video()
    settings.project = None
    settings.task = None
    settings.save()
    click.echo(f"Stopped work")


@click.command("config")
@click.argument("home_dir", default=settings.home_dir)
@click.argument("target_dir", default=settings.target_dir)
@click.argument("interval", default=settings.interval)
def set_config(
    home_dir=settings.home_dir,
    target_dir=settings.target_dir,
    interval: int = settings.interval,
):
    """Set config.json"""
    Settings(
        home_dir=home_dir,
        target_dir=target_dir,
        interval=interval,
        project=settings.project,
        task=settings.task,
    ).save()


@click.group()
def cli():
    pass


cli.add_command(startwork)
cli.add_command(stopwork)
cli.add_command(set_config)