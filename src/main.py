import os
import json
from itertools import cycle
import xml.etree.ElementTree as ET

import requests
from rich import print
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
BASE_URL = "https://parentportal.ormiston.school.nz/api/api.php"
DEFAULT_HEADERS = {
    "User-Agent": "MOYAI Moment",
    "Origin": "file://",
    "X-Requested-With": "nz.co.KAMAR",
}
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")


class Period(BaseModel):
    period_time: str
    class_name: str


class Day(BaseModel):
    name: str
    start: str
    end: str
    periods: list[Period]


class Week(BaseModel):
    week_number: int
    days: list[Day]


def login(username, password):

    data = {
        "Command": "Logon",
        "Key": "vtku",
        "Username": username,
        "Password": password,
    }

    login_response = requests.post(BASE_URL, headers=DEFAULT_HEADERS, data=data)
    if login_response.status_code != 200:
        raise Exception(f"Failed to login!\nAPI Response: {login_response.text}")

    login_response_parsed = ET.fromstring(login_response.text)

    key = login_response_parsed.find("Key")

    if key is None or key.text is None:
        raise Exception(f"Failed to login!\nAPI Response: {login_response.text}")

    return key.text


def timetable(key: str, username: str, use_cache: bool = True):
    cache_path = os.path.join(CACHE_DIR, "timetable.xml")
    if use_cache and os.path.exists(cache_path):
        print("Using cached timetable...")
        tree = ET.parse(cache_path)
        timetable_response_parsed = tree.getroot()
    else:
        print("Fetching timetable...")
        data = {
            "Command": "GetStudentTimetable",
            "Key": key,
            "StudentID": username,
            "Grid": "2023TT",
        }

        timetable_response = requests.post(BASE_URL, headers=DEFAULT_HEADERS, data=data)
        if timetable_response.status_code != 200:
            raise Exception("Failed to get timetable")

        timetable_response_parsed = ET.fromstring(timetable_response.text)

        with open(cache_path, "w") as f:
            f.write(timetable_response.text)

    if (students_tag := timetable_response_parsed.find("Students")) is None:
        raise Exception("Smth went wrong idk tbh")
    if (timetable_data := students_tag[0].find("TimetableData")) is None:
        raise Exception("Smth went wrong idk tbh")

    period_times = periods(key)

    weeks_list: list[list[dict[str, str]]] = []
    for week in timetable_data[3:]:
        classes_per_day = [i.text.strip().split("|")[1:-1] for i in week]  # type: ignore
        days = zip(period_times, classes_per_day)
        days = list(map(lambda day: dict(zip(*day)), days))
        weeks_list.append(days)

    weeks = []
    weeks_json = {}

    week_counter = 1
    for week in weeks_list:
        day_names = cycle(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        days = []
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
            days.append(day)

        week = Week(week_number=week_counter, days=days)
        weeks.append(week)
        weeks_json[f"W{week_counter}"] = json.loads(week.json())

        week_counter += 1

    with open(os.path.join(CACHE_DIR, "timetable.json"), "w") as f:
        print("timetable saved as json")
        json.dump(weeks_json, f, indent=4)


def periods(key: str, use_cache: bool = True):
    cache_path = os.path.join(CACHE_DIR, "periods.xml")
    if use_cache and os.path.exists(cache_path):
        print("Using cached periods...")
        tree = ET.parse(cache_path)
        periods_parsed = tree.getroot()
    else:
        print("Fetching periods...")
        data = {
            "Command": "GetGlobals",
            "Key": key,
        }

        periods_response = requests.post(BASE_URL, headers=DEFAULT_HEADERS, data=data)
        if periods_response.status_code != 200:
            raise Exception("Failed to get periods")

        periods_parsed = ET.fromstring(periods_response.text)

        with open(cache_path, "w") as f:
            f.write(periods_response.text)

    # code for period names (might use later or delete)
    # if (definitions := periods_parsed.find("PeriodDefinitions")) is None:
    #     raise Exception("Smth went wrong idk tbh")
    # period_names = {}
    # for definition in definitions:
    #     key = definition.find("PeriodTime").text  # type: ignore
    #     value = definition.find("PeriodName").text  # type: ignore
    #     if key is None or value is None:
    #         continue
    #     period_names[key] = value

    if (start_times := periods_parsed.find("StartTimes")) is None:
        raise Exception("Smth went wrong idk tbh")

    day_start_times = [[period.text for period in day] for day in start_times]
    return day_start_times


def main():
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")

    if USERNAME is None or PASSWORD is None:
        raise Exception("username and password should both be in the env file")

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    key = login(USERNAME, PASSWORD)
    timetable(key, USERNAME)


if __name__ == "__main__":
    main()
