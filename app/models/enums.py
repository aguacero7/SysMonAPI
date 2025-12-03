from enum import Enum

class ComputerStatus(int, Enum):
    ON = 1
    OFF = 0
    RELOADING = 2

class EquipmentType(str, Enum):
    ORDINATEUR = "ordinateur"
    ROUTER = "router"
