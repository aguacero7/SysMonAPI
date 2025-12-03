from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator
from .enums import ComputerStatus, EquipmentType
import re
import socket
import os

class EquipementBase(SQLModel):
    type_equipement: EquipmentType
    mac: str = Field(index=True, unique=True)
    ip: str = Field(index=True, unique=True)
    hostname: str = ""
    status: ComputerStatus
    joignable: bool = False

    @field_validator('mac')
    def validate_mac(cls, v: str) -> str:
        mac_pattern = r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('Invalid MAC address format.')
        return v.upper()

    @field_validator('ip')
    def validate_ip(cls, v: str) -> str:
        ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, v):
            raise ValueError('Invalid IP address format.')
        return v

    @model_validator(mode='after')
    def autoset_fields(self):
        if not self.hostname:
            try:
                self.hostname = socket.gethostbyaddr(self.ip)[0]
            except socket.herror:
                self.hostname = None

        if self.joignable == False:
            try:
                ping_target = self.hostname if self.hostname else self.ip
                response = os.system(f"ping -c 1 -W 1 {ping_target} > /dev/null 2>&1")
                self.joignable = (response == 0)
            except Exception:
                self.joignable = False

        return self
