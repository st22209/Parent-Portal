import os
import json
from itertools import cycle
import xml.etree.ElementTree as ET

from rich.progress import track

from core.consts import CACHE_DIR
from core.models import Week, Day, Period


def periods(start_times: ET.Element) -> list[list[str | None]]:
    return [[period.text for period in day] for day in start_times]


def timetable(timetable_data: ET.Element, period_data: ET.Element) -> list[Week]:
    period_times = periods(period_data)

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
        days_list: list[Day] = []
        for day in week:
            classes: list[Period] = []
            for period_time, period_class in day.items():
                if period_time is None:
                    continue
                period = Period(period_time=period_time, class_name=period_class)
                classes.append(period)
            day = Day(
                name=next(day_names),
                start=classes[0].period_time,
                end=classes[-1].period_time,
                periods=classes,
            )
            days_list.append(day)

        week = Week(week_number=week_counter, days=days_list)
        weeks.append(week)
        weeks_json[f"W{week_counter}"] = json.loads(week.json())
        week_counter += 1

    with open(os.path.join(CACHE_DIR, "timetable.json"), "w") as f:
        print("timetable saved as json")
        json.dump(weeks_json, f, indent=4)

    return weeks
