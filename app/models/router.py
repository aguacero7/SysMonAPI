import json
from sqlmodel import Field
from typing import Optional
from .equipement import EquipementBase
from .enums import EquipmentType
from .ssh_connection import SSHConnection

class Router(EquipementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_equipement: EquipmentType = Field(default=EquipmentType.ROUTER)
    bgp_enabled: bool = False
    ospf_enabled: bool = False
    rip_enabled: bool = False
    frrouting_version: Optional[str] = ""
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
    def query_ntp(self) -> dict:
        import json
        import subprocess

        command = f"/usr/local/bin/rkik {self.ip} -jv"
        result = subprocess.run(command,shell=True,capture_output=True,text=True,timeout=10)

        stdout = result.stdout
        stderr = result.stderr
        if not result.returncode  ==0:
            return {"success": False, "message":stdout}
        ntp_data = json.loads(stdout)
        return {"success": True, "ntp_data": ntp_data}
    def execute_vtysh_command(self, command: str) -> dict:
        ssh_conn = self.get_ssh_connection()
        if not ssh_conn:
            None

        stdout, stderr, exit_code = ssh_conn.execute_command(f"vtysh -c '{command}'")

        if exit_code != 0:
            return None

        return stdout

    def get_routing_table(self) -> dict:
        return self.execute_vtysh_command("show ip route json")

    def get_bgp_summary(self) -> dict:
        return self.execute_vtysh_command("show ip bgp summary json")

    def get_ospf_neighbors(self) -> dict:
        return self.execute_vtysh_command("show ip ospf neighbor json")

    def get_interfaces_status(self) -> dict:
        return self.execute_vtysh_command("show interface brief json")
