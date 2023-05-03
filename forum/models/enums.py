"""Module provides Enum type"""
from enum import Enum


class TagType(Enum):
    '''Defines Enum of tags to be used by Post model'''
    SCIENCE = 'Science'
    MATH = 'Math'
    PROGRAMMING = 'Programming'
    HISTORY = 'History'

    def __repr__(self) -> str:
        return self.value


class Role(Enum):
    '''Defines Enum of role types to be used by User model'''
    DEFAULT = "DEFAULT"
    ADMIN = "ADMIN"

    def __str__(self) -> str:
        return self.value


class VoteType(Enum):
    UP = 1
    DOWN = -1
