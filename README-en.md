# FastAPI Network Equipment Management API with JWT Authentication

[![GitHub](https://img.shields.io/badge/GitHub-aguacero7%2FSysMonAPI-blue?logo=github)](https://github.com/aguacero7/SysMonAPI)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)

Modern and secure REST API for comprehensive management and monitoring of computers and network routers. This solution provides real-time monitoring via SSH and SNMP, with JWT authentication to secure all access.

## Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [SNMP Monitoring](#-snmp-monitoring)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Test Environment](#-test-environment)
- [Solved Issues](#-solved-issues)
- [Contributing](#-contributing)

## Features

### Authentication and Security
- **JWT Authentication** - Complete API security with JWT tokens
- **User Management** - User system with roles (admin, standard user)
- **Endpoint Protection** - All sensitive endpoints require authentication

### Computer Monitoring (via SSH)
- **Real-time System Monitoring**
  - CPU usage (system load)
  - Memory consumption (available/used RAM)
  - Operating system information
- **Secure SSH Connection** - Encrypted communication with remote servers
- **Full CRUD Management** - Create, read, update, and delete computers

### Router Monitoring (via SSH & SNMP)
- **Advanced Network Monitoring**
  - Routing tables (IPv4/IPv6 routes)
  - BGP status (Border Gateway Protocol)
  - OSPF neighbors (Open Shortest Path First)
  - Network interface status
  - NTP synchronization (Network Time Protocol)
- **Real-time SNMP Monitoring**
  - Automatic metric collection every 60 seconds
  - Availability and response time
  - Bandwidth statistics (inbound/outbound traffic)
  - Network error detection and counting
  - Uptime and operational status
- **Monitoring Dashboard** - Web interface to visualize metrics

### Database
- **PostgreSQL** - Robust relational database
- **SQLModel** - Modern ORM based on Pydantic and SQLAlchemy
- **Alembic Migrations** - Database schema evolution management

## 🏗️ Architecture

The application uses a layered architecture:

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  (REST Endpoints + JWT Authentication)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Services Layer                  │
│  - SSH Connections (Paramiko)           │
│  - SNMP Monitor (Background Task)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Data Layer                      │
│  - SQLModel ORM                         │
│  - PostgreSQL Database                  │
└─────────────────────────────────────────┘
```

## Installation

### Quick Installation with Docker (Recommended)

The simplest way to start the application with all its services:

```bash
# Clone the repository
git clone https://github.com/aguacero7/SysMonAPI.git
cd TD-FASTAPI

# Start all services (API, Database, Test servers, Router)
docker compose up -d

# Verify services are running
docker compose ps
```

The API will be accessible at:
- **Main API**: http://localhost:8000/
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **SNMP Dashboard**: http://localhost:8000/monitoring/dashboard

### Local Installation

#### Prerequisites
- Python 3.11 or higher
- PostgreSQL 16 or higher
- pip or Poetry for dependency management

#### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/aguacero7/SysMonAPI.git
cd TD-FASTAPI
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure PostgreSQL database**
```bash
# Create the database
createdb apidb

# Set the connection URL
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/apidb"
```

5. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+psycopg2://user:mdpsecret@database:5432/apidb` |
| `JWT_SECRET_KEY` | Secret key for JWT (optional) | Auto-generated |
| `JWT_ALGORITHM` | JWT algorithm (optional) | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration (optional) | `30` |

### Database Configuration

For local installation with PostgreSQL:

```bash
export DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/database_name"
```

For Docker (configured in `docker-compose.yml`):
```yaml
environment:
  - DATABASE_URL=postgresql+psycopg2://user:mdpsecret@database:5432/apidb
```

### SNMP Configuration

SNMP monitoring is configured for:
- **Collection interval**: 60 seconds
- **SNMP version**: v2c
- **Community string**: public (configurable in `config/snmpd.conf`)
- **Timeout**: 5 seconds per request

## 📘 Usage

### Create an Admin User

```bash
# With Docker
docker exec -it fastapi-app python create_admin.py

# Locally
python create_admin.py
```

### Authentication

1. **Get a JWT token**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

2. **Use the token in requests**
```bash
curl -X GET "http://localhost:8000/ordinateurs" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Add Equipment

**Add a computer:**
```bash
curl -X POST "http://localhost:8000/ordinateurs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "172.230.0.10",
    "hostname": "test-server-1",
    "ssh_username": "root",
    "ssh_password": "testpass123",
    "ssh_port": 22
  }'
```

**Add a router:**
```bash
curl -X POST "http://localhost:8000/routers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "172.230.0.20",
    "hostname": "test-router-1",
    "ssh_username": "root",
    "ssh_password": "testpass123",
    "ssh_port": 22
  }'
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Create a new user | No |
| POST | `/auth/login` | Login and get a JWT token | No |
| GET | `/auth/me` | Get current user information | Yes |

### Computers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/ordinateurs` | List all computers | Yes |
| GET | `/ordinateurs/{id}` | Get computer details | Yes |
| POST | `/ordinateurs` | Create a computer | Yes |
| PUT | `/ordinateurs/{id}` | Update a computer | Yes |
| DELETE | `/ordinateurs/{id}` | Delete a computer | Yes |
| GET | `/ordinateurs/{id}/memory` | Get available memory via SSH | Yes |
| GET | `/ordinateurs/{id}/cpu_load` | Get CPU load via SSH | Yes |
| GET | `/ordinateurs/{id}/os_release` | Get system information via SSH | Yes |

### Routers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/routers` | List all routers | Yes |
| GET | `/routers/{id}` | Get router details | Yes |
| POST | `/routers` | Create a router | Yes |
| PUT | `/routers/{id}` | Update a router | Yes |
| DELETE | `/routers/{id}` | Delete a router | Yes |
| GET | `/routers/{id}/routing_table` | Get routing table via SSH | Yes |
| GET | `/routers/{id}/bgp_summary` | Get BGP summary via SSH | Yes |
| GET | `/routers/{id}/ospf_neighbors` | Get OSPF neighbors via SSH | Yes |
| GET | `/routers/{id}/interfaces` | Get interface status via SSH | Yes |
| GET | `/routers/{id}/query_ntp` | Get NTP information via SSH | Yes |

### Equipment

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/equipements` | List all equipment (computers + routers) | Yes |
| GET | `/equipements/search?ip={ip}` | Search equipment by IP | Yes |

### SNMP Monitoring

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/monitoring/routers/{id}/metrics` | All SNMP metrics for a router | Yes |
| GET | `/monitoring/routers/{id}/availability` | Availability statistics | Yes |
| GET | `/monitoring/routers/{id}/bandwidth` | Bandwidth statistics | Yes |
| GET | `/monitoring/routers/{id}/errors` | Network error statistics | Yes |
| GET | `/monitoring/overview` | Overview of all routers | Yes |
| GET | `/monitoring/dashboard` | Interactive HTML dashboard | No |

## 📊 SNMP Monitoring

### How It Works

The SNMP monitoring system runs as a background task:

1. **Automatic Collection**: Every 60 seconds, the service polls each router
2. **Collected Metrics**:
   - Availability (SNMP ping)
   - Response time
   - System uptime
   - Network traffic (inbound/outbound bytes)
   - Network errors (inbound/outbound errors)
   - Interface operational status
3. **Storage**: Metrics are stored in the PostgreSQL database
4. **History**: Complete history retention for analysis and graphs

### Monitoring Dashboard

Access the web dashboard at http://localhost:8000/monitoring/dashboard to view:
- Real-time status of all routers
- 24-hour availability
- Average response time
- System uptime
- Visual indicators (UP/DOWN routers)

### Query Examples

**Get metrics for the last 24 hours:**
```bash
curl "http://localhost:8000/monitoring/routers/1/metrics?hours=24&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Calculate availability over a week:**
```bash
curl "http://localhost:8000/monitoring/routers/1/availability?hours=168" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get bandwidth statistics:**
```bash
curl "http://localhost:8000/monitoring/routers/1/bandwidth?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Project Structure

```
TD-FASTAPI/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py              # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py                 # Enumerations (equipment types, etc.)
│   │   ├── equipement.py            # Base Equipment model
│   │   ├── ordinateur.py            # Computer model (inherits from Equipment)
│   │   ├── router.py                # Router model (inherits from Equipment)
│   │   ├── ssh_connection.py        # SSH connection model
│   │   └── snmp_metric.py           # SNMP metrics model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ordinateurs.py           # Computer endpoints
│   │   ├── routers.py               # Router endpoints
│   │   ├── equipements.py           # Generic equipment endpoints
│   │   └── snmp_monitoring.py       # SNMP monitoring endpoints
│   ├── services/
│   │   └── snmp_monitor.py          # SNMP monitoring service (background task)
│   ├── templates/
│   │   └── dashboard.html           # Dashboard HTML template
│   └── main.py                      # Application entry point
├── config/
│   ├── snmpd.conf                   # SNMP configuration for router
│   └── chrony.conf                  # NTP configuration for router
├── frr-config/
│   ├── frr.conf                     # FRRouting configuration (BGP, OSPF)
│   └── vtysh.conf                   # VTY shell configuration
├── bruno/                           # API testing collection (Postman alternative)
├── requirements.txt                 # Python dependencies
├── create_admin.py                  # Admin user creation script
├── docker-compose.yml               # Service orchestration
├── Dockerfile                       # Docker image for FastAPI app
├── Dockerfile.router                # Custom Docker image for FRR router
└── README.md                        # Project documentation
```

## 🛠️ Technologies Used

| Category | Technologies |
|----------|--------------|
| **Web Framework** | FastAPI 0.115.0, Uvicorn (ASGI server) |
| **Database** | PostgreSQL 16, SQLModel, psycopg2 |
| **Authentication** | JWT (JSON Web Tokens) |
| **SSH Connection** | Paramiko 3.4.0 |
| **SNMP Monitoring** | easysnmp 0.2.6 |
| **Templates** | Jinja2 3.1.2 |
| **Validation** | Pydantic 2.9.0 |
| **Containerization** | Docker, Docker Compose |
| **Router** | FRRouting (FRR) - BGP, OSPF, RIP |

## 🧪 Test Environment

The complete test environment is deployed via Docker Compose and includes:

### Test Architecture

```
┌─────────────────────────────────────────────────┐
│         Docker Network: 172.230.0.0/24          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐     ┌──────────────┐         │
│  │ test-server-1│     │ test-server-2│         │
│  │ 172.230.0.10 │     │ 172.230.0.11 │         │
│  │ SSH: 22      │     │ SSH: 22      │         │
│  └──────────────┘     └──────────────┘         │
│                                                 │
│         ┌──────────────────────┐                │
│         │  router (FRR)        │                │
│         │  172.230.0.20        │                │
│         │  SSH: 22             │                │
│         │  SNMP: 161           │                │
│         └──────────────────────┘                │
│                                                 │
│  ┌──────────────┐     ┌──────────────┐         │
│  │ fastapi-app  │     │  database    │         │
│  │ 172.230.0.3  │────▶│ 172.230.0.2  │         │
│  │ Port: 8000   │     │ PostgreSQL   │         │
│  └──────────────┘     └──────────────┘         │
└─────────────────────────────────────────────────┘
```

### Deployed Services

1. **database (PostgreSQL 16)**
   - IP: 172.230.0.2
   - Database for storing equipment and metrics

2. **fastapi-app**
   - IP: 172.230.0.3
   - Port: 8000 (exposed on host)
   - Main FastAPI application

3. **test-server-1 & test-server-2**
   - IPs: 172.230.0.10 and 172.230.0.11
   - Python servers with SSH enabled
   - Credentials: root / testpass123
   - Used for testing computer monitoring

4. **router (FRRouting)**
   - IP: 172.230.0.20
   - Custom image with FRR, SNMP, and NTP
   - Protocols: BGP, OSPF, RIP
   - SNMP v2c enabled (community: public)
   - SSH Credentials: root / testpass123

### Useful Commands

```bash
# Start the complete environment
docker compose up -d

# View API logs
docker compose logs -f fastapi-app

# Access the router via SSH
docker exec -it router vtysh

# Test SNMP manually
docker exec -it fastapi-app snmpwalk -v2c -c public 172.230.0.20 system

# Restart a service
docker compose restart fastapi-app

# Stop everything
docker compose down
```

## 🔍 Solved Issues

### 1. Router Deletion with SNMP Metrics

**Problem**: When adding SNMP monitoring, router deletion failed due to the foreign key relationship between `routers` and `snmp_metrics` tables.

**Solution**: Added cascade delete in the SQLModel model to automatically clean up all associated metrics before deleting a router.

```python
# In app/models/snmp_metric.py
router_id: int = Field(foreign_key="router.id", ondelete="CASCADE")
```

### 2. Obsolete FRRouting Docker Image

**Problem**: The official `frrouting/frr:latest` image didn't work properly and hadn't been maintained for 2 years.

**Solution**: Created a custom Docker image ([Dockerfile.router](Dockerfile.router)) based on Ubuntu with:
- Manual FRRouting installation from official repositories
- SNMP configuration with snmpd
- NTP configuration with chrony
- Secure SSH configuration

### 3. Mounted Configuration File Permissions

**Problem**: The container executed `chown` on mounted configuration files, making it impossible to modify them from the local user.

**Solution**:
- Use of named volumes for persistent data
- Configuration files are copied instead of being directly mounted
- Alternative: permission adjustment with the `:ro` (read-only) option for configs

## 📚 Interactive Documentation

Once the application is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive interface to test all endpoints
  - Integrated JWT authentication
  - Detailed request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - More readable alternative documentation
  - Ideal for consultation

- **SNMP Dashboard**: http://localhost:8000/monitoring/dashboard
  - Real-time monitoring web interface
  - Overview of all routers
  - Graphs and statistics

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed for educational purposes.

## 👤 Author

**aguacero7**
- GitHub: [@aguacero7](https://github.com/aguacero7)
- Repository: [SysMonAPI](https://github.com/aguacero7/SysMonAPI)

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [FRRouting Documentation](https://docs.frrouting.org)
- [SNMP Protocol](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
- [JWT Introduction](https://jwt.io/introduction)
