import os
from datetime import date
from typing import Optional
import xml.etree.ElementTree as ET

import requests

from kmrpp.core.consts import BASE_URL, DEFAULT_HEADERS, CACHE_DIR
from kmrpp.core.exceptions import FailedToLogin, FailedToFetchTimetable

YEAR = date.today().year


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ParentPortal(metaclass=Singleton):
    def __init__(self, username: str, password: str, key: Optional[str] = None) -> None:
        self.username = username
        self.password = password

        self.key = self.__login() if key is None else key

    def timetable(self, use_cache: bool = True) -> ET.Element:
        cache_path = os.path.join(CACHE_DIR, "timetable.xml")

        if use_cache and os.path.exists(cache_path):
            print("Using cached timetable...")
            tree = ET.parse(cache_path)
            timetable_response_parsed = tree.getroot()
        else:
            print("Fetching timetable...")
            data = {
                "Command": "GetStudentTimetable",
                "Key": self.key,
                "StudentID": self.username,
                "Grid": f"{YEAR}TT",
            }

            timetable_response = requests.post(
                BASE_URL, headers=DEFAULT_HEADERS, data=data
            )
            if timetable_response.status_code != 200:
                raise FailedToFetchTimetable

            timetable_response_parsed = ET.fromstring(timetable_response.text)

            # cache timetable for future
            with open(cache_path, "w") as f:
                f.write(timetable_response.text)

        if (students_tag := timetable_response_parsed.find("Students")) is None:
            raise FailedToFetchTimetable
        if (timetable_data := students_tag[0].find("TimetableData")) is None:
            raise FailedToFetchTimetable

        return timetable_data

    def periods(self, use_cache: bool = True) -> ET.Element:
        cache_path = os.path.join(CACHE_DIR, "periods.xml")
        if use_cache and os.path.exists(cache_path):
            print("Using cached periods...")
            tree = ET.parse(cache_path)
            periods_parsed = tree.getroot()
        else:
            print("Fetching periods...")
            data = {
                "Command": "GetGlobals",
                "Key": self.key,
            }

            periods_response = requests.post(
                BASE_URL, headers=DEFAULT_HEADERS, data=data
            )
            if periods_response.status_code != 200:
                raise Exception("Failed to get periods")

            periods_parsed = ET.fromstring(periods_response.text)

            with open(cache_path, "w") as f:
                f.write(periods_response.text)

        if (start_times := periods_parsed.find("StartTimes")) is None:
            raise Exception("Failed to get periods")

        return start_times

    def calendar(self, use_cache: bool = True) -> ET.Element:
        cache_path = os.path.join(CACHE_DIR, "calendar.xml")
        if use_cache and os.path.exists(cache_path):
            print("Using cached calendar...")
            tree = ET.parse(cache_path)
            calendar_parsed = tree.getroot()
        else:
            print("Fetching calendar...")
            data = {
                "Command": "GetCalendar",
                "Key": self.key,
                "Year": YEAR,
            }

            calendar_response = requests.post(
                BASE_URL, headers=DEFAULT_HEADERS, data=data
            )
            if calendar_response.status_code != 200:
                raise Exception("Failed to get calendar")

            calendar_parsed = ET.fromstring(calendar_response.text)

            with open(cache_path, "w") as f:
                f.write(calendar_response.text)

        if (days := calendar_parsed.find("Days")) is None:
            raise Exception("Failed to get calendar")

        return days

    def __login(self) -> str:
        data = {
            "Command": "Logon",
            "Key": "vtku",
            "Username": self.username,
            "Password": self.password,
        }

        login_response = requests.post(BASE_URL, headers=DEFAULT_HEADERS, data=data)
        if login_response.status_code != 200:
            raise FailedToLogin(login_response.text)

        key = ET.fromstring(login_response.text).find("Key")
        if key is None or key.text is None:
            raise FailedToLogin(login_response.text)

        return key.text
