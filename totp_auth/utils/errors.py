from enum import StrEnum


class FieldErrorList(StrEnum):
    NOT_DIGIT = "NOT_DIGIT"
    NOT_FILLED = "NOT_FILLED"
    INCORRECT_LENGTH = "INCORRECT_LENGTH"
    EMAIL_NOT_VALID = "EMAIL_NOT_VALID"


class FieldError(Exception):
    def __init__(self, error: FieldErrorList):
        self.error = error


class InvalidCredentials(Exception):
    pass


class InvalidFields(Exception):
    pass
