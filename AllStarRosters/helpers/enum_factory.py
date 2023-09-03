from enum import Enum, auto


# =================================================================================================================== #

class FileType(Enum):
    HTML = auto()
    JSON = auto()
    SQL = auto()
    INI = auto()


class MovingRangeCalc(Enum):
    MAX = auto()
    MEAN = auto()
    MIN = auto()


class DatabankDataType(Enum):
    ALLSTAR = 'AllstarFull'
    APPEARANCES = 'Appearances'
    AWARDS = 'AwardsSharePlayers'
    COLLEGE = 'CollegePlaying'
    HOF = 'HallOfFame'
    MANAGERS = 'Managers'
    PEOPLE = 'People'
    SALARIES = 'Salaries'
    TEAMS = 'Teams'
    REG_BATTING = 'Batting'
    REG_FIELDING = 'Fielding'
    POST_BATTING = 'BattingPost'
    POST_FIELDING = 'FieldingPost'


# =================================================================================================================== #
"""Enums for bigquery utilities"""


class CreateDisposition(Enum):
    IF_NEEDED = 'CREATE_IF_NEEDED'
    NEVER = 'CREATE_NEVER'


class WriteDisposition(Enum):
    APPEND = 'WRITE_APPEND'
    EMPTY = 'WRITE_EMPTY'
    TRUNCATE = 'WRITE_TRUNCATE'


class Priority(Enum):
    INTERACTIVE = 'INTERACTIVE'
    BATCH = 'BATCH'


# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
