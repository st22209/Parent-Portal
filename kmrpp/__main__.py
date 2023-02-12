import os
import json
from datetime import datetime

import typer
from rich import box
from rich import print
from rich.table import Table
from dotenv import load_dotenv

from kmrpp.core.models import Weekdays
from kmrpp.core.parse import timetable
from kmrpp.core.consts import CACHE_DIR
from kmrpp.core.http import ParentPortal


def get_portal() -> ParentPortal:
    load_dotenv()

    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if username is None or password is None:
        raise Exception("Please set username and password with login command")
    return ParentPortal(username, password)


app = typer.Typer()


@app.command("timetable-to-json")
def timetable_to_json():
    p = get_portal()
    timetable(p.timetable(), p.periods())

    print(
        f"[green]Timetable converted to json and saved to: {os.path.join(CACHE_DIR, 'timetable.json')}"
    )


@app.command("timetable-json")
def timetable_json(
    week: int = typer.Option(
        ..., help="The number of the week you want the timetable for"
    ),
    day: Weekdays = typer.Option(
        None,
    ),
):
    print(f"[bold blue]Showing timetable for W{week}:")

    path = os.path.join(CACHE_DIR, "timetable.json")
    if not os.path.exists(path):
        p = get_portal()
        timetable(p.timetable(), p.periods())

    with open(path) as f:
        data = json.load(f)

    try:
        week_data = data[f"W{week}"]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")

    if day is None:
        return print(week_data)
    print(week_data["days"][day.value])


@app.command("timetable")
def timetable_table(
    week: int = typer.Option(
        ..., help="The number of the week you want the timetable for"
    ),
):
    path = os.path.join(CACHE_DIR, "timetable.json")
    if not os.path.exists(path):
        p = get_portal()
        timetable(p.timetable(), p.periods())

    with open(path) as f:
        data = json.load(f)

    try:
        week_data = data[f"W{week}"]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    table = Table(
        title=f"[bold blue]Timetable - Week: {week}", box=box.HEAVY, show_lines=True
    )
    table.add_column("Time")
    for dayname in weekdays:
        table.add_column(dayname)

    times = []
    for day in week_data["days"].values():
        for i in day["periods"]:
            times.append(i["period_time"])
    times = list(
        map(
            lambda x: datetime.strftime(x, "%H:%M"),
            sorted(map(lambda x: datetime.strptime(x, "%H:%M"), set(times))),
        )
    )
    row_data = {i: [] for i in times}
    for k in row_data:
        for data in week_data["days"].values():
            found = False
            for i in data["periods"]:
                if i["period_time"] == k:
                    row_data[k].append(" ".join(i["class_name"].split("-")[2:]))
                    found = True
            if not found:
                row_data[k].append(None)
    for ptime, pclass in row_data.items():
        table.add_row(ptime, *pclass)
    print(table)
    print(
        "[red]Empty boxes are most likely break, before/after school or the continuation of a class"
    )


@app.command()
def login(
    username: str = typer.Option(
        ..., help="The username that you use on parent portal"
    ),
    password: str = typer.Option(
        ...,
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
        help="The password that you use on parent portal",
    ),
):
    with open(os.path.join(os.path.dirname(__file__), "..", ".env"), "w") as f:
        f.write(f'USERNAME = "{username}"\nPASSWORD = "{password}"')

    print("[bold green]username and password successfully stored!")


def main():
    app()


if __name__ == "__main__":
    main()
