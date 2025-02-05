from enum import StrEnum
from pathlib import Path


class FieldErrorList(StrEnum):
    NOT_DIGIT = "NOT_DIGIT"
    NOT_FILLED = "NOT_FILLED"
    INCORRECT_LENGTH = "INCORRECT_LENGTH"
    EMAIL_NOT_VALID = "EMAIL_NOT_VALID"


class FieldError(Exception):
    def __init__(self, error: FieldErrorList, field_name: str):
        self.error = error
        self.field_name = field_name


class InvalidCredentials(Exception):
    pass


class InvalidFields(Exception):
    pass


class LoaderError(Exception):
    def __init__(self, file_path: Path, error: Exception):
        self.file_path = file_path
        self.error = error
