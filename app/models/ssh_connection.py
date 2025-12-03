from pydantic import BaseModel
from typing import Optional
import paramiko

class SSHConnection(BaseModel):
    hostname: Optional[str] = None
    username: str
    password: Optional[str] = None
    key_filename: Optional[str] = None
    port: int = 22

    def execute_command(self, command: str) -> tuple[str, str, int]:
        try:
            client = paramiko.SSHClient()

            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(self.hostname, self.port, self.username, self.password, key_filename=self.key_filename)
            stdin, stdout, stderr = client.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()
            result = stdout.read().decode(), stderr.read().decode(), exit_code
            client.close()
            return result
        except Exception as e:
            return "", str(e), -1
