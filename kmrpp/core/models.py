""" (module) models
This module contains models that are used to handle data
"""

from enum import Enum

from pydantic import BaseModel


class Period(BaseModel):
    """
    A period

    Attributes:
        period_time (str): The time at which the period starts
        class_name (str): The class at that period
    """

    period_time: str
    class_name: str


class Day(BaseModel):
    """
    A day object

    Attributes:
        name (str): The weekday name eg "Monday"
        start (str): The time at which school starts that day
        end (str): The time at which school ends that day
        periods (list[Period]): A list of periods/classes that day
    """

    name: str
    start: str
    end: str
    periods: list[Period]


class Week(BaseModel):
    """
    A week object

    Attributes:
        week_number (int): The week's number in the timetable
        day (dict[str, Day]): a dict of days in the week
            the key is a weekday like "Monday" or "Thursday" and value is a Day object
    """

    week_number: int
    days: dict[str, Day]


class Weekdays(Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
