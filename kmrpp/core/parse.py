# type: ignore
""" (module) parse
This module contains parsing functions to make things like xml data easier to work with
"""

import os
import json
from itertools import cycle
from datetime import datetime
import xml.etree.ElementTree as ET

from rich import box
from rich import print
from rich.table import Table
from rich.progress import track

from kmrpp.core.consts import CACHE_DIR
from kmrpp.core.models import Week, Day, Period


def parse_periods(start_times: ET.Element) -> list[list[str]]:
    """
    This function parses periods from xml to a python list

    Returns:
        list[list[str]]: The start times for all periods
    """
    return [[period.text for period in day] for day in start_times]


def parse_timetable(timetable_data: ET.Element, period_data: ET.Element) -> list[Week]:
    """
    This function parses the xml timetable and period data into a list of Week objects
    It also converts the data into json which is stored in the cache dir

    Returns:
        list[Week]: A list of week objects
    """
    period_times = parse_periods(period_data)

    weeks_list: list[list[dict[str, str]]] = []
    for week in timetable_data[3:]:
        classes_per_day = [i.text.strip().split("|")[1:-1] for i in week]
        days = zip(period_times, classes_per_day)
        days = list(map(lambda day: dict(zip(*day)), days))
        weeks_list.append(days)

    weeks: list[Week] = []
    weeks_json = {}

    week_counter = 1
    for week in track(weeks_list, description="Converting Weeks..."):
        day_names = cycle(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        days_list: dict[str, Day] = {}
        for day in week:
            classes: list[Period] = []
            for period_time, period_class in day.items():
                if period_time is None:
                    continue
                period = Period(period_time=period_time, class_name=period_class)
                classes.append(period)
            weekday = next(day_names)
            day = Day(
                name=weekday,
                start=classes[0].period_time,
                end=classes[-1].period_time,
                periods=classes,
            )
            days_list[weekday] = day

        week = Week(week_number=week_counter, days=days_list)
        weeks.append(week)
        weeks_json[f"W{week_counter}"] = json.loads(week.json())
        week_counter += 1

    with open(os.path.join(CACHE_DIR, "timetable.json"), "w") as f:
        print("[b green]✓ Timetable saved as JSON")
        json.dump(weeks_json, f, indent=4)

    return weeks


def timetable_to_table(week_data: dict, week: int, dates: list[str]) -> Table:
    """
    This function converts json data about the weeks timetable to a table
    This table will be rendered by rich to the terminal

    Returns:
        rich.Table: The table object
    """
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    table = Table(
        title=f"[bold blue]Timetable - Week: {week}", box=box.HEAVY, show_lines=True
    )
    table.add_column("Time")
    for dayname, date in zip(weekdays, dates):
        table.add_column(f"{dayname} ({'/'.join(date.split('-')[1:][::-1])})")

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
                    rdata = i["class_name"].split("-")[2:]
                    if rdata:
                        c, t, p = rdata
                        row_data[k].append(f"{c} - {t} - {p}")
                    else:
                        row_data[k].append("")
                    found = True
            if not found:
                row_data[k].append(None)
    for ptime, pclass in row_data.items():
        table.add_row(ptime, *pclass)

    return table


def parse_calendar(calendar_data: ET.Element) -> None:
    """
    This function parses the calendar and saves it as JSON in the cache dir
    """
    data = {"days": {}, "weeks": {}}

    for day in calendar_data:
        data["days"][day.find("Date").text] = {
            "status": day.find("Status").text,
            "week": day.find("WeekYear").text,
            "term": day.find("Term").text,
            "weekday": day.find("DayTT").text,
            "term_week": day.find("Week").text,
        }

        if (week := day.find("WeekYear").text) is None:
            continue

        if data["weeks"].get(week) is None:
            data["weeks"][week] = []

        data["weeks"][week].append(
            {
                "date": day.find("Date").text,
                "status": day.find("Status").text,
                "term": day.find("Term").text,
                "weekday": day.find("DayTT").text,
                "term_week": day.find("Week").text,
            }
        )

    with open(os.path.join(CACHE_DIR, "calendar.json"), "w") as f:
        print("[b green]✓ Calendar saved as JSON")
        json.dump(data, f, indent=4)

    return data
