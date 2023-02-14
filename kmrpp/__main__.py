""" (script) __main__
This is the script that runs the cli
"""

import os
import json
from datetime import datetime

import typer
from rich import print
from rich.json import JSON
from dotenv import load_dotenv

from kmrpp.core.models import Weekdays
from kmrpp.core.consts import CACHE_DIR
from kmrpp.core.http import ParentPortal
from kmrpp.core.exceptions import NoLoginDetails
from kmrpp.core.parse import parse_timetable, timetable_to_table, parse_calendar


load_dotenv()


def get_portal() -> ParentPortal:
    """
    Get login details and use them to return the ParentPortal singleton object

    Returns:
        ParentPortal: The object used to carry out http requets to the api
    Raises:
        NoLoginDetails: If login details are not found
    """

    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if username is None or password is None:
        raise NoLoginDetails
    return ParentPortal(username, password)


app = typer.Typer()


@app.command("ttjson", hidden=True, help="Alias for the 'timetable-to-json' command")
@app.command(
    "timetable-to-json",
    hidden=True,
    help="Convert entire terminal to json and give link to file (alias: 'ttjson')",
)
def timetable_to_json():
    portal = get_portal()
    timetable_data = portal.timetable()
    period_data = portal.periods()
    parse_timetable(timetable_data, period_data)

    print(
        f"[green]Timetable converted to json and saved to: {os.path.join(CACHE_DIR, 'timetable.json')} :tick:"
    )


@app.command("tj", hidden=True, help="Alias for the 'timetable-json' command")
@app.command("timetable-json", help="View timetable in json format, (alias: 'tt')")
def timetable_json(
    week: int = typer.Option(
        ..., help="The number of the week you want the timetable for"
    ),
    day: Weekdays = typer.Option(
        None,
        autocompletion=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ),
    cache: bool = typer.Option(
        True, help="If set to true, it will refetch data instead of using cache"
    ),
):
    print(f"[bold blue]Showing timetable for W{week}:")

    path = os.path.join(CACHE_DIR, "timetable.json")
    if not os.path.exists(path) or cache is False:
        portal = get_portal()
        timetable_data = portal.timetable(cache)
        period_data = portal.periods(cache)
        parse_timetable(timetable_data, period_data)

    with open(path) as f:
        data = json.load(f)

    try:
        week_data = data[f"W{week}"]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")

    if day is None:
        return print(JSON(json.dumps(week_data)))
    print(JSON(json.dumps(week_data["days"][day.value])))


@app.command("tt", hidden=True, help="Alias for the 'timetable' command")
@app.command("timetable", help="View you timetable as a Table (alias: 'tt')")
def timetable_table(
    week: int = typer.Option(
        None, help="The number of the week you want the timetable for"
    ),
    cache: bool = typer.Option(
        True, help="If this option is used it will refetch data instead of using cache"
    ),
):
    timetable_path = os.path.join(CACHE_DIR, "timetable.json")
    portal = get_portal()
    if not os.path.exists(timetable_path) or not cache:
        timetable_data = portal.timetable(cache)
        period_data = portal.periods(cache)
        parse_timetable(timetable_data, period_data)

    with open(timetable_path) as f:
        timetable_data = json.load(f)

    calendar_path = os.path.join(CACHE_DIR, "calendar.json")
    if not os.path.exists(calendar_path) or not cache:
        calendar_data = portal.calendar(cache)
        parse_calendar(calendar_data)

    with open(calendar_path) as f:
        calendar_data = json.load(f)

    if week is None:
        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        day_data = calendar_data["days"].get(date)
        if day_data is None or day_data.get("week") is None:
            return print(
                f"[bold red]Was not able to get current week!\nPlease specify week with [blue]`--week`"
            )
        week = day_data["week"]

    try:
        week_data = timetable_data[f"W{week}"]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")
    try:
        calendar_data = calendar_data["weeks"][str(week)]
    except KeyError:
        return print(f"[bold red]Timetable data for week {week} was not found")

    dates = [i["date"] for i in calendar_data][1:-1]
    table = timetable_to_table(week_data, week, dates)
    print(table)
    print(
        "[red]Empty boxes are most likely break, before/after school or the continuation of a class"
    )


@app.command("l", hidden=True, help="Alias for the 'login' command")
@app.command(help="Command to log you into parent portal (alias: 'l')")
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

    print("[bold green]Username and Password successfully stored!")

    # fetch data to cache
    portal = get_portal()
    portal.timetable(use_cache=False)
    portal.periods(use_cache=False)
    portal.calendar(use_cache=False)


def main():
    app()


if __name__ == "__main__":
    main()
