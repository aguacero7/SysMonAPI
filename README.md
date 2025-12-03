# API FastAPI - Gestion d'Équipements Réseau avec Authentification JWT

API REST sécurisée pour la gestion et la supervision d'ordinateurs et de routeurs réseau avec support SSH et authentification JWT.

## Fonctionnalités

- **Authentification JWT** - Sécurisation de l'API avec tokens JWT
- **Gestion des utilisateurs** - Système d'utilisateurs avec rôles admin
- **Supervision d'ordinateurs** - Monitoring CPU, mémoire, système via SSH
- **Supervision de routeurs** - Tables de routage, BGP, OSPF, interfaces
- **Migrations de base de données** - Gestion avec Alembic
- **Gestion des dépendances** - Poetry et requirements.txt

## Installation rapide avec Docker

```bash
docker compose up
```

L'API sera accessible sur http://localhost:8000/

## Configuration locale

### Installation des dépendances

Avec pip:
```bash
pip install -r requirements.txt
```

### Configuration de la base de données

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/apidb"
```
### Ordinateurs (authentification requise)

- `GET /ordinateurs` - Liste tous les ordinateurs
- `GET /ordinateurs/{id}` - Détails d'un ordinateur
- `POST /ordinateurs` - Créer un ordinateur
- `PUT /ordinateurs/{id}` - Modifier un ordinateur
- `DELETE /ordinateurs/{id}` - Supprimer un ordinateur
- `GET /ordinateurs/{id}/memory` - Mémoire disponible
- `GET /ordinateurs/{id}/cpu_load` - Charge CPU
- `GET /ordinateurs/{id}/os_release` - Infos système

### Routeurs (authentification requise)

- `GET /routers` - Liste tous les routeurs
- `GET /routers/{id}` - Détails d'un routeur
- `POST /routers` - Créer un routeur
- `PUT /routers/{id}` - Modifier un routeur
- `DELETE /routers/{id}` - Supprimer un routeur
- `GET /routers/{id}/routing_table` - Table de routage
- `GET /routers/{id}/bgp_summary` - Résumé BGP
- `GET /routers/{id}/ospf_neighbors` - Voisins OSPF
- `GET /routers/{id}/interfaces` - État des interfaces
- `GET /routers/{id}/query_ntp` - Informations NTP

### Équipements (authentification requise)

- `GET /equipements` - Liste tous les équipements
- `GET /equipements/search?ip={ip}` - Rechercher par IP
## Documentation interactive

Une fois l'application lancée, accédez à:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Structure du projet

```
TD-FASTAPI/
|
├── app/
│   ├── config/
│   │   ├── database.py         # Configuration BDD
│   ├── models/
│   │   ├── enums.py
│   │   ├── equipement.py
│   │   ├── ordinateur.py
│   │   ├── router.py
│   │   └── ssh_connection.py
│   ├── routers/
│   │   ├── ordinateurs.py
│   │   ├── routers.py
│   │   └── equipements.py
│   └── main.py
├── requirements.txt            # Dépendances pip
├── create_admin.py             # Script création admin
├── docker-compose.yml
└── Dockerfile
```

## Variables d'environnement

- `DATABASE_URL` - URL de connexion PostgreSQL (défaut: postgresql+psycopg2://user:mdpsecret@database:5432/apidb)


## Environnement de test

L'environnement de test est un docker compose qui nous met à disposition un routeur ainsi que 2 serveurs,
L'infra est définie dans `docker-compose.yml`, le Dockerfile du routeur est disponible dans Dockerfile.router.

