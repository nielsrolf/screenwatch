import calendar
import datetime as dt
import os
import subprocess

import click
import pandas as pd

from screenwatch.configure import Settings, get_todos, get_work_logs, settings
from screenwatch.watch import main as watch


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
        },
        ignore_index=True,
    )
    df.to_csv(settings.work_logs, index=False)
    settings.project = project
    settings.task = task
    settings.save()
    click.echo(f"Started work on {project} {task}")
    # In the background, run the watch script
    watch()


@click.command("stop")
def stopwork():
    _stopwork()


# Command to add todos for the day and track how many percent get done
@click.command("today")
@click.argument("tasks", nargs=-1)
def add_todos_for_today(tasks):
    deadline = pd.Timestamp.now().replace(hour=23, minute=59, second=59)
    for task in tasks:
        add_task(task, deadline=deadline)
    show_todos(deadline)


def add_task(task, deadline):
    df = get_todos()
    df = df.append(
        {
            "task": task,
            "registered": pd.Timestamp.now(),
            "deadline": deadline,
            "done": None,
        },
        ignore_index=True,
    )
    df.to_csv(settings.todos, index=False)
    click.echo(f"Added task: {task}")


@click.command("todo")
def todo():
    """Show todo tasks"""
    # tomorrow 0:00
    deadline = pd.Timestamp.now().replace(hour=23, minute=59, second=59) + pd.Timedelta(
        minutes=1
    )
    show_todos(deadline)


def get_human_readable_date(date):
    # get deadline in human readable format: "today", "tomorrow", "Monday", etc - after one week show the date without time
    if date.date() == pd.Timestamp.now().date():
        return "today"
    elif date.date() == (pd.Timestamp.now() + pd.Timedelta(days=1)).date():
        return "tomorrow"
    elif date.date() < (pd.Timestamp.now() + pd.Timedelta(days=7)).date():
        return calendar.day_name[date.weekday()]
    else:
        return date.date()


def show_todos(deadline):
    df = get_todos().sort_values("deadline")
    # Overdue, unfinished tasks
    overdue = df[df.deadline < pd.Timestamp.now()]
    overdue = overdue[overdue.done.isnull()]
    click.echo(f"Overdue tasks")
    for _, row in overdue.iterrows():
        click.echo(f"    {row.task}")
    click.echo("-" * 80)
    # todo tasks until deadline
    todo = df[df.deadline <= deadline]
    todo = todo[todo.done.isnull()]

    click.echo(f"Todo tasks until {get_human_readable_date(deadline)}")
    for _, row in todo.iterrows():
        click.echo(f"    {row.task}")
    click.echo("-" * 80)
    # done tasks with deadline > now
    done = df[df.deadline > pd.Timestamp.now()]
    done = done[done.done.notnull()]
    click.echo(f"Done tasks")
    for _, row in done.iterrows():
        click.echo(f"    {row.task}")
    click.echo("-" * 80)


@click.command("done")
@click.argument("tasks", nargs=-1)
def mark_tasks_as_done(tasks):
    df = get_todos()
    for task in tasks:
        df.loc[df.task == task, "done"] = pd.Timestamp.now()
    df.to_csv(settings.todos, index=False)
    click.echo(f"Marked tasks as done: {tasks}")


@click.command("cancel")
@click.argument("tasks", nargs=-1)
def cancel_tasks(tasks):
    df = get_todos()
    for task in tasks:
        df = df[df.task != task]
    df.to_csv(settings.todos, index=False)
    click.echo(f"Canceled tasks: {tasks}")


def get_next_date_of(target_weekday):
    today = dt.datetime.now().date()
    weekday = calendar.day_name[today.weekday()].lower()

    day_names = {name.lower(): i for i, name in enumerate(calendar.day_name)}
    target_weekday_index = day_names[target_weekday]

    if weekday == target_weekday:
        next_target_weekday = today + dt.timedelta(days=7)
    else:
        days_to_next_target_weekday = (target_weekday_index - today.weekday()) % 7
        next_target_weekday = today + dt.timedelta(days=days_to_next_target_weekday)
    # make sure the time is 23:59:59
    next_target_weekday = pd.Timestamp(next_target_weekday).replace(
        hour=23, minute=59, second=59
    )
    return next_target_weekday


@click.command("plan")
@click.argument("day", type=str)
@click.argument("tasks", nargs=-1)
def plan_tasks(day, tasks):
    """Plan tasks for a specific day. Day can be a date or a weekday."""
    if day[:3] in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        deadline = get_next_date_of(day)
        for task in tasks:
            add_task(task, deadline=deadline)
    elif day == "tomorrow":
        deadline = pd.Timestamp.now().replace(
            hour=23, minute=59, second=59
        ) + pd.Timedelta(hours=24)
        for task in tasks:
            add_task(task, deadline=deadline)
    else:
        # parse the day as a date
        deadline = pd.Timestamp(day)
        for task in tasks:
            add_task(task, deadline=deadline)
    show_todos(deadline)


@click.command("what")
def what():
    if settings.project is None:
        # print nice message with cool smiley
        click.echo("You are not working on anything right now")
        return
    click.echo(f"You are working on \n{settings.project}\n    {settings.task}")


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
@click.option("--home_dir", default=settings.home_dir)
@click.option("--target_dir", default=settings.target_dir)
@click.option("--interval", default=settings.interval)
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
        python=subprocess.check_output(["which", "python"]).decode().strip(),
    ).save()


@click.group()
def cli():
    pass


cli.add_command(startwork)
cli.add_command(stopwork)
cli.add_command(set_config)
cli.add_command(what)
cli.add_command(add_todos_for_today)
cli.add_command(mark_tasks_as_done)
cli.add_command(todo)
cli.add_command(cancel_tasks)
cli.add_command(plan_tasks)
