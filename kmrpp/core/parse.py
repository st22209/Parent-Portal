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


def parse_periods(start_times: ET.Element) -> list[list[str | None]]:
    return [[period.text for period in day] for day in start_times]


def parse_timetable(timetable_data: ET.Element, period_data: ET.Element) -> list[Week]:
    period_times = parse_periods(period_data)

    weeks_list: list[list[dict[str, str]]] = []
    for week in timetable_data[3:]:
        classes_per_day = [i.text.strip().split("|")[1:-1] for i in week]  # type: ignore
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
        print("timetable saved as json")
        json.dump(weeks_json, f, indent=4)

    return weeks


def timetable_to_table(week_data: dict, week: int):
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

    return table


def parse_calendar(calendar_data: ET.Element):
    days = {
        day.find("Date").text: {  # type: ignore
            "status": day.find("Status").text,  # type: ignore
            "week": day.find("WeekYear").text,  # type: ignore
            "term": day.find("Term").text,  # type: ignore
            "term_week": day.find("Week").text,  # type: ignore
        }
        for day in calendar_data
    }
    return days
