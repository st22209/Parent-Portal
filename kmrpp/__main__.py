import os
import json

import typer
from rich import print
from dotenv import load_dotenv

from kmrpp.core.models import Weekdays
from kmrpp.core.consts import CACHE_DIR
from kmrpp.core.http import ParentPortal
from kmrpp.core.parse import parse_timetable, timetable_to_table


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
    portal = get_portal()
    timetable_data = portal.timetable()
    period_data = portal.periods()
    parse_timetable(timetable_data, period_data)

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
        portal = get_portal()
        timetable_data = portal.timetable()
        period_data = portal.periods()
        parse_timetable(timetable_data, period_data)

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
        portal = get_portal()
        timetable_data = portal.timetable()
        period_data = portal.periods()
        parse_timetable(timetable_data, period_data)

    with open(path) as f:
        data = json.load(f)

    try:
        week_data = data[f"W{week}"]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")

    table = timetable_to_table(week_data, week)
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

    # fetch data to cache
    portal = get_portal()
    portal.timetable(use_cache=False)
    portal.periods(use_cache=False)
    portal.calendar(use_cache=False)


def main():
    app()


if __name__ == "__main__":
    main()
