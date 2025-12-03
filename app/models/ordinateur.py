from sqlmodel import Field
from typing import Optional
from .equipement import EquipementBase
from .enums import EquipmentType
from .ssh_connection import SSHConnection
import os
import re

class Ordinateur(EquipementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_equipement: EquipmentType = Field(default=EquipmentType.ORDINATEUR)
    taille_disque: int
    os: str
    ram: float = 0.0

    ssh_hostname: Optional[str] = None
    ssh_username: Optional[str] = None
    ssh_password: Optional[str] = None
    ssh_key_filename: Optional[str] = None
    ssh_port: int = 22

    def get_ssh_connection(self) -> Optional[SSHConnection]:
        if self.ssh_username:
            return SSHConnection(
                hostname=self.ssh_hostname or self.ip,
                username=self.ssh_username,
                password=self.ssh_password,
                key_filename=self.ssh_key_filename,
                port=self.ssh_port
            )
        return None

    def get_free_memory(self) -> float:
        ssh_conn = self.get_ssh_connection()
        if ssh_conn:
            stdout, stderr, exit_code = ssh_conn.execute_command("free -m")
            if exit_code == 0:
                return float(stdout.strip().split('\n')[1].split()[3]) / 1024
        else:
            cmd_output = os.popen("free -m").readlines()
            return float(cmd_output[1].split()[3]) / 1024
        return 0.0

    def get_max_memory(self) -> float:
        ssh_conn = self.get_ssh_connection()
        if ssh_conn:
            stdout, stderr, exit_code = ssh_conn.execute_command("free -m")
            if exit_code == 0:
                return float(stdout.strip().split('\n')[1].split()[1]) / 1024
        else:
            cmd_output = os.popen("free -m").readlines()
            return float(cmd_output[1].split()[1]) / 1024
        return 0.0

    def get_cpu_load(self) -> float:
        ssh_conn = self.get_ssh_connection()
        if ssh_conn:
            stdout, stderr, exit_code = ssh_conn.execute_command("top -bn1 | grep 'Cpu(s)'")
            if exit_code == 0:
                cpu_idle = float(re.findall(r'(\d+\.\d+)\s*id', stdout)[0])
                return 100.0 - cpu_idle
        else:
            cmd_output = os.popen("top -bn1 | grep 'Cpu(s)'").readline()
            cpu_idle = float(re.findall(r'(\d+\.\d+)\s*id', cmd_output)[0])
            return 100.0 - cpu_idle
        return 0.0

    def get_os_release(self) -> dict:
        ssh_conn = self.get_ssh_connection()
        if not ssh_conn:
            return {"success": False, "error": "SSH credentials not configured"}

        stdout, stderr, exit_code = ssh_conn.execute_command("cat /etc/os-release")

        if exit_code != 0:
            return {"success": False, "error": stderr}

        os_info = {}
        for line in stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                os_info[key] = value.strip('"')

        return {"success": True, "os_release": os_info}
