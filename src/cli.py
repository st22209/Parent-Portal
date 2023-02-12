import os
import json

import typer
from rich import print
from dotenv import load_dotenv

from core.parse import timetable
from core.consts import CACHE_DIR
from core.http import ParentPortal


def get_portal() -> ParentPortal:
    load_dotenv()

    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")

    if username is None or password is None:
        raise Exception("Please set username and password with login command")
    return ParentPortal(username, password)


app = typer.Typer()


@app.command("timetable-to-json")
def timetable_json():
    p = get_portal()
    timetable(p.timetable(), p.periods())


@app.command("timetable")
def timetable_table(
    week: int = typer.Option(
        ..., help="The number of the week you want the timetable for"
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

    print(week_data)


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


if __name__ == "__main__":
    app()
