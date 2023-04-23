from functools import wraps
from flask_login import current_user
from flask import current_app
from enum import Enum


class Role(Enum):
    STUDENT = "STUDENT"
    PROFESSOR = "PROFESSOR"
    ADMIN = "ADMIN"

    def __str__(self) -> str:
        return self.value
