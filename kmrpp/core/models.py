from enum import Enum

from pydantic import BaseModel


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
    days: dict[str, Day]


class Weekdays(Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
