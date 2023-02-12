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
    days: list[Day]
