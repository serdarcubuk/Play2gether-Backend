from enum import Enum


class Sort(str, Enum):
    ID = "id"
    GAME_NAME = "game_name"
    CREATE_DATE = "create_date"
    UPDATE_DATE = "update_date"


class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"
