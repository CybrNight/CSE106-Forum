from functools import wraps
from flask_login import current_user
from flask import current_app
from enum import Enum


class Role(Enum):
    DEFAULT = "DEFAULT"
    PROFESSOR = "PROFESSOR"
    ADMIN = "ADMIN"

    def __str__(self) -> str:
        return self.value


class TagType(Enum):
    SCIENCE = 'Science'
    MATH = 'Math'
    PROGRAMMING = 'Programming'
    HISTORY = 'History'

    def __repr__(self) -> str:
        return self.value
