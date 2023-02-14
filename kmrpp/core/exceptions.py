""" (module) exceptions
This module contains exceptions that will be raised by the app
"""

from rich.text import Text
from rich.panel import Panel
from rich.console import Console


class BaseException(Exception):
    """Base class for other exceptions to inherit form"""

    pass


class RichBaseException(BaseException):
    """
    Base rich class for other exceptions to inherit form
    This one prints the error to console with rich
    """

    def __init__(self, title: str, message: str) -> None:
        error_message = Panel(
            Text.from_markup(f"[yellow]{message}"),
            title=title,
            border_style="red",
        )
        Console().print(error_message, justify="left")
        exit(1)


class FailedToLogin(RichBaseException):
    """
    Raised when the script fails to login
    """

    def __init__(self, api_response: str) -> None:
        super().__init__(
            "Failed To Login!",
            f"Could not login to parent portal\nAPI Response:{api_response}",
        )


class NoLoginDetails(RichBaseException):
    """
    Raised when login details could not be found
    """

    def __init__(self) -> None:
        super().__init__(
            "Could not find login details!",
            "Please set the username and password with the login command\nExample: [blue]kmr login --username person123",
        )


class FailedToFetch(RichBaseException):
    """
    Raised when the app fails to fetch data
    """

    def __init__(self, thing: str) -> None:
        super().__init__(
            f"Failed To Get {thing}!",
            f"{thing} could not be fetched for unknown reasons",
        )
