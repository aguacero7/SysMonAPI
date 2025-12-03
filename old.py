from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator, model_validator
from enum import Enum
import re
import json, os
import socket
import paramiko
from typing import Optional, Literal, Union, Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
class ComputerStatus(str, Enum):
    ON = 1
    OFF = 0
    RELOADING = 2

class EquipmentType(str, Enum):
    ORDINATEUR = "ordinateur"
    ROUTER = "router"

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:mdpsecret@localhost:5432/apidb")
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=3600)

def get_session():
    with Session(engine) as session:
        yield session

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


class Router(EquipementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_equipement: EquipmentType = Field(default=EquipmentType.ROUTER)
    frrouting_version: str = ""
    bgp_enabled: bool = False
    ospf_enabled: bool = False
    rip_enabled: bool = False

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

    def get_routing_table(self) -> dict:
        ssh_conn = self.get_ssh_connection()
        if not ssh_conn:
            return {"success": False, "error": "SSH credentials not configured"}

        stdout, stderr, exit_code = ssh_conn.execute_command("vtysh -c 'show ip route'")

        if exit_code != 0:
            return {"success": False, "error": stderr}

        return {"success": True, "routing_table": stdout}

    def execute_vtysh_command(self, command: str) -> dict:
        ssh_conn = self.get_ssh_connection()
        if not ssh_conn:
            return {"success": False, "error": "SSH credentials not configured"}

        stdout, stderr, exit_code = ssh_conn.execute_command(f"vtysh -c '{command}'")

        if exit_code != 0:
            return {"success": False, "error": stderr}

        return {"success": True, "output": stdout}



def init_db():
    import time
    for i in range(5):
        try:
            SQLModel.metadata.create_all(engine)
            return
        except Exception as e:
            if i < 4:
                time.sleep(5)
            else:
                raise

@app.on_event("startup")
def startup_event():
    init_db()
    
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API FastAPI"}

@app.get("/ordinateurs")
def get_ordinateurs(session: Session = Depends(get_session)):
    statement = select(Ordinateur)
    ordinateurs = session.exec(statement).all()
    return ordinateurs

@app.post("/add_ordinateur")
def add_ordinateur(ordinateur: Ordinateur, session: Session = Depends(get_session)):
    session.add(ordinateur)
    session.commit()
    session.refresh(ordinateur)
    return {"message": "Ordinateur added successfully", "id": ordinateur.id}

@app.put("/edit_ordinateur/{ordinateur_id}")
def edit_ordinateur(ordinateur_id: int, ordinateur_data: Ordinateur, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    ordinateur_dict = ordinateur_data.model_dump(exclude_unset=True, exclude={'id'})
    for key, value in ordinateur_dict.items():
        setattr(ordinateur, key, value)

    session.add(ordinateur)
    session.commit()
    session.refresh(ordinateur)
    return {"message": "Ordinateur updated successfully", "ordinateur": ordinateur}

@app.delete("/delete_ordinateur/{ordinateur_id}")
def delete_ordinateur(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    session.delete(ordinateur)
    session.commit()
    return {"message": "Ordinateur deleted successfully"}

@app.get("/ordinateur/{ordinateur_id}")
def get_ordinateur(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")
    return ordinateur

@app.get("/memory/{ordinateur_id}")
def get_memory(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    total_memory = ordinateur.get_max_memory()
    free_memory = ordinateur.get_free_memory()
    return {"free_memory": free_memory, "total_memory": total_memory}

@app.get("/cpu_load/{ordinateur_id}")
def get_cpu_load(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    cpu_load = ordinateur.get_cpu_load()
    return {"cpu_load": cpu_load}

@app.get("/os_release/{ordinateur_id}")
def get_os_release(ordinateur_id: int, session: Session = Depends(get_session)):
    ordinateur = session.get(Ordinateur, ordinateur_id)
    if not ordinateur:
        raise HTTPException(status_code=404, detail="Ordinateur not found")

    return ordinateur.get_os_release()

@app.get("/equipements")
def get_equipements(session: Session = Depends(get_session)):
    ordinateurs = session.exec(select(Ordinateur)).all()
    routers = session.exec(select(Router)).all()
    return {"ordinateurs": ordinateurs, "routers": routers}

@app.get("/equipements/search")
def search_equipement_by_ip(ip: str, session: Session = Depends(get_session)):
    ordinateur = session.exec(select(Ordinateur).where(Ordinateur.ip == ip)).first()
    if ordinateur:
        return {"type": "ordinateur", "data": ordinateur}

    router = session.exec(select(Router).where(Router.ip == ip)).first()
    if router:
        return {"type": "router", "data": router}

    raise HTTPException(status_code=404, detail="Equipement not found")


@app.get("/routers")
def get_routers(session: Session = Depends(get_session)):
    statement = select(Router)
    routers = session.exec(statement).all()
    return routers

@app.post("/add_router")
def add_router(router: Router, session: Session = Depends(get_session)):
    session.add(router)
    session.commit()
    session.refresh(router)
    return {"message": "Router added successfully", "id": router.id}

@app.get("/router/{router_id}")
def get_router(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router

@app.put("/edit_router/{router_id}")
def edit_router(router_id: int, router_data: Router, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")

    router_dict = router_data.model_dump(exclude_unset=True, exclude={'id'})
    for key, value in router_dict.items():
        setattr(router, key, value)

    session.add(router)
    session.commit()
    session.refresh(router)
    return {"message": "Router updated successfully", "router": router}

@app.delete("/delete_router/{router_id}")
def delete_router(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")

    session.delete(router)
    session.commit()
    return {"message": "Router deleted successfully"}

@app.get("/router/routing_table/{router_id}")
def get_routing_table(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router.get_routing_table()

@app.get("/router/bgp_summary/{router_id}")
def get_bgp_summary(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router.get_bgp_summary()

@app.get("/router/ospf_neighbors/{router_id}")
def get_ospf_neighbors(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router.get_ospf_neighbors()

@app.get("/router/interfaces/{router_id}")
def get_interfaces(router_id: int, session: Session = Depends(get_session)):
    router = session.get(Router, router_id)
    if not router:
        raise HTTPException(status_code=404, detail="Router not found")
    return router.get_interfaces_status()
