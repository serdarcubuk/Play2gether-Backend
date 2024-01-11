from enum import Enum


class Sort(str, Enum):
    ID = "id"
    ROOM_NAME = "room_name"
    CREATE_DATE = "create_date"
    UPDATE_DATE = "update_date"


class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"
