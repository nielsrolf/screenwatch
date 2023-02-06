"""
# Plots to show:
- percentage of todos done per day
- time spent on each project per day
- time spent on each task per day
- distribution of time spent on each project in the last 7 days
"""

import pandas as pd
from plotly import express as px

from screenwatch.configure import get_todos, get_work_logs


def plot_todos():
    """Plot:
    - number of tasks done per day
    - number of overdue tasks per day
    """
    df = get_todos()
    df["overdue"] = (df["deadline"] < pd.Timestamp.now()) & (df["done"].isnull()) | (
        df["done"] > df["deadline"]
    )
    # for each day, count the number of tasks done and overdue
    # create a new dataframe where each task is copied to each day between (registered, max(done, now))
    daily = pd.DataFrame()
    for _, row in df.iterrows():
        if row["done"] is not None:
            end = row["done"]
        else:
            end = pd.Timestamp.now()
        days = pd.date_range(row["registered"], end, freq="D")
        for day in days:
            done = 1 if day <= row["done"] else 0
            overdue = 1 if not done and day > row["deadline"] else 0
            daily = daily.append(
                {
                    "day": day,
                    "done": done,
                    "overdue": overdue,
                },
                ignore_index=True,
            )
    daily = daily.groupby("day").sum()
    daily = daily.reset_index()
    fig = px.line(daily, x="day", y=["done", "overdue"])
    fig.show()


def plot_work_logs():
    """Plot:
    - time spent on each project per day
    - time spent on each task per day
    - distribution of time spent on each project in the last 7 days
    """
    df = get_work_logs()
    df["duration"] = df["end"] - df["start"]
    df["day"] = df["start"].dt.date
    # time spent on each project per day (stacked bar plot)
    daily = df.groupby(["day", "project"]).sum().reset_index()
    fig = px.bar(daily, x="day", y="duration", color="project", barmode="stack")
    fig.show()
    # time spent on each task per day (stacked bar plot)
    daily = df.groupby(["day", "project", "task"]).sum().reset_index()
    fig = px.bar(daily, x="day", y="duration", color="task", barmode="stack")
    fig.show()
    # distribution of time spent on each project in the last 7 days (pie chart)
    weekly = df[df["day"] > pd.Timestamp.now().date() - pd.Timedelta(days=7)]
    weekly = weekly.groupby("project").sum().reset_index()
    fig = px.pie(weekly, values="duration", names="project")
    fig.show()
