import discord
from typing import Literal, Optional

"""This file contains all custom exceptions that the bot may raise."""

class CommandException(Exception):
    """
    An exception that occurs when a command is invoked incorrectly.

    Should only be used internally to represent exception error severity.
    """

    ErrorLevel = Literal["error", "warning", "info"]
    error_colour = {
        "error": discord.Colour.red(), 
        "warning": discord.Colour.yellow(), 
        "info": discord.Colour.light_grey()
    }

    def __init__(
        self, 
        error: ErrorLevel, 
        *args, **kwargs
    ):
        self.error = self.error_colour[error]

    # TODO: There's probably a better way to send error messages
    # by storing the error messages inside the exceptions themselves
    def to_embed(
        self, 
        message: str, jump_url: Optional[str] = ''
    ) -> discord.Embed:
        """Formats exceptions into Discord-style embeds."""

        if jump_url:
            jump_url = f'\n[Jump]({jump_url})'
        return discord.Embed(
            title=type.capitalize(),
            description=message+jump_url,
            colour=self.error
        )


# TODO: I don't actually know which category these errors are,
# so this should be sorted out - Sera
class NotUser(CommandException):
    """Raised when ID given is not a valid user."""

    def __init__(self, *args, **kwargs):
        super().__init__("error", *args, **kwargs)

class DuplicateUnit(CommandException):
    """Raised when duplicate units are found in a giveaway duration."""

    def __init__(self, *args, **kwargs):
        super().__init__("warning", *args, **kwargs)

class DisallowedChars(CommandException):
    """Raised when disallowed characters are found in a giveaway duration."""

    def __init__(self, *args, **kwargs):
        super().__init__("warning", *args, **kwargs)

class NoPrecedingValue(CommandException):
    """Raised when no digits precede a unit in a giveaway duration."""

    def __init__(self, *args, **kwargs):
        super().__init__("info", *args, **kwargs)

class IncorrectCommandFormat(CommandException):
    """Raised when the command format is invalid."""

    def __init__(self, *args, **kwargs):
        super().__init__("error", *args, **kwargs)
