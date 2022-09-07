"""This file contains all custom exceptions that the bot may raise."""

# TODO: Consider creating a custom exception to subclass off of, so every
# error can represent themselves as a discord embed

class NotUser(Exception):
    """This exception is raised when the input is not a valid user."""
    pass

class DuplicateUnit(Exception):
    pass

class DisallowedChars(Exception):
    pass

class NoPrecedingValue(Exception):
    pass

class IncorrectCommandFormat(Exception):
    """This exception is raised when the command format is invalid."""
    pass
