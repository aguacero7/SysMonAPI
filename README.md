# API FastAPI - Gestion d'Équipements Réseau

[![GitHub](https://img.shields.io/badge/GitHub-aguacero7%2FSysMonAPI-blue?logo=github)](https://github.com/aguacero7/SysMonAPI)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org)

API REST moderne pour la gestion et la supervision complète d'ordinateurs et de routeurs réseau. Cette solution offre un monitoring en temps réel via SSH et SNMP.

## Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Tutoriel - Effectuer des tests](#-tutoriel)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)
- [Monitoring SNMP](#-monitoring-snmp)
- [Structure du projet](#-structure-du-projet)
- [Technologies utilisées](#-technologies-utilisées)
- [Environnement de test](#-environnement-de-test)
- [Problèmes résolus](#-problèmes-résolus)
- [Contribution](#-contribution)

## Fonctionnalités

### Supervision d'Ordinateurs (via SSH)
- **Monitoring système en temps réel**
  - Utilisation CPU (charge système)
  - Consommation mémoire (RAM disponible/utilisée)
  - Informations système d'exploitation
- **Connexion SSH sécurisée** - Communication cryptée avec les serveurs distants
- **Gestion CRUD complète** - Création, lecture, mise à jour et suppression d'ordinateurs

### Supervision de Routeurs (via SSH & SNMP)
- **Monitoring réseau avancé**
  - Tables de routage (routes IPv4/IPv6)
  - État BGP (Border Gateway Protocol)
  - Voisins OSPF (Open Shortest Path First)
  - État des interfaces réseau
  - Synchronisation NTP (Network Time Protocol)
- **Monitoring SNMP en temps réel**
  - Collecte automatique de métriques toutes les 60 secondes
  - Disponibilité et temps de réponse
  - Statistiques de bande passante (trafic entrant/sortant)
  - Détection et comptage d'erreurs réseau
  - Uptime et état opérationnel
- **Dashboard de monitoring** - Interface web pour visualiser les métriques

### Base de données
- **PostgreSQL** - Base de données relationnelle robuste
- **SQLModel** - ORM moderne basé sur Pydantic et SQLAlchemy

## Architecture

L'application utilise une architecture en couches :

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│           (Endpoints REST)              │
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

### Installation rapide avec Docker (Recommandé)

La méthode la plus simple pour démarrer l'application avec tous ses services :

```bash
# Clone le repository
git clone https://github.com/aguacero7/SysMonAPI.git
cd TD-FASTAPI

# Démarrer tous les services (API, Base de données, Serveurs de test, Routeur)
docker compose up -d

# Vérifier que les services sont démarrés
docker compose ps
```

L'API sera accessible sur :
- **API principale** : http://localhost:8000/
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc
- **Dashboard SNMP** : http://localhost:8000/monitoring/dashboard (interface web avec graphiques en temps réel)

### Installation locale

#### Prérequis
- Python 3.11 ou supérieur
- PostgreSQL 16 ou supérieur
- pip ou Poetry pour la gestion des dépendances

#### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/aguacero7/SysMonAPI.git
cd TD-FASTAPI
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données PostgreSQL**
```bash
# Créer la base de données
createdb apidb

# Définir l'URL de connexion
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/apidb"
```

5. **Lancer l'application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
## Tutoriel
Pour tester l'application, il suffira de simplement lancer le docker compose (voir étape ci-dessus), 
Puis d'ouvrir dans bruno tous les fichiers .bru présents dans le dossier bruno.

> **Et c'est TOUT !!!**
## Configuration

### Variables d'environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql+psycopg2://user:mdpsecret@database:5432/apidb` |

### Configuration de la base de données

Pour une installation locale avec PostgreSQL :

```bash
export DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/database_name"
```

Pour Docker (configuré dans `docker-compose.yml`) :
```yaml
environment:
  - DATABASE_URL=postgresql+psycopg2://user:mdpsecret@database:5432/apidb
```

### Configuration SNMP

Le monitoring SNMP est configuré pour :
- **Intervalle de collecte** : 60 secondes
- **Version SNMP** : v2c
- **Community string** : public (configurable dans `config/snmpd.conf`)
- **Timeout** : 5 secondes par requête

## Utilisation

### Ajouter un équipement

**Ajouter un ordinateur :**
```bash
curl -X POST "http://localhost:8000/ordinateurs" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "172.230.0.10",
    "hostname": "test-server-1",
    "ssh_username": "root",
    "ssh_password": "testpass123",
    "ssh_port": 22
  }'
```

**Ajouter un routeur :**
```bash
curl -X POST "http://localhost:8000/routers" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "172.230.0.20",
    "hostname": "test-router-1",
    "ssh_username": "root",
    "ssh_password": "testpass123",
    "ssh_port": 22
  }'
```

## API Endpoints

### Ordinateurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/ordinateurs` | Liste tous les ordinateurs |
| GET | `/ordinateurs/{id}` | Détails d'un ordinateur |
| POST | `/ordinateurs` | Créer un ordinateur |
| PUT | `/ordinateurs/{id}` | Modifier un ordinateur |
| DELETE | `/ordinateurs/{id}` | Supprimer un ordinateur |
| GET | `/ordinateurs/{id}/memory` | Obtenir la mémoire disponible via SSH |
| GET | `/ordinateurs/{id}/cpu_load` | Obtenir la charge CPU via SSH |
| GET | `/ordinateurs/{id}/os_release` | Obtenir les infos système via SSH |

### Routeurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/routers` | Liste tous les routeurs |
| GET | `/routers/{id}` | Détails d'un routeur |
| POST | `/routers` | Créer un routeur |
| PUT | `/routers/{id}` | Modifier un routeur |
| DELETE | `/routers/{id}` | Supprimer un routeur |
| GET | `/routers/{id}/routing_table` | Table de routage via SSH |
| GET | `/routers/{id}/bgp_summary` | Résumé BGP via SSH |
| GET | `/routers/{id}/ospf_neighbors` | Voisins OSPF via SSH |
| GET | `/routers/{id}/interfaces` | État des interfaces via SSH |
| GET | `/routers/{id}/query_ntp` | Informations NTP via SSH |

### Équipements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/equipements` | Liste tous les équipements (ordinateurs + routeurs) |
| GET | `/equipements/search?ip={ip}` | Rechercher un équipement par IP |

### Monitoring SNMP

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/monitoring/routers/{id}/metrics` | Toutes les métriques SNMP d'un routeur |
| GET | `/monitoring/routers/{id}/availability` | Statistiques de disponibilité |
| GET | `/monitoring/routers/{id}/bandwidth` | Statistiques de bande passante |
| GET | `/monitoring/routers/{id}/errors` | Statistiques d'erreurs réseau |
| GET | `/monitoring/overview` | Vue d'ensemble de tous les routeurs |
| GET | `/monitoring/dashboard` | Dashboard HTML interactif |

## Monitoring SNMP

### Fonctionnement

Le système de monitoring SNMP fonctionne en tâche de fond (background task) :

1. **Collecte automatique** : Toutes les 60 secondes, le service interroge chaque routeur
2. **Métriques collectées** :
   - Disponibilité (ping SNMP)
   - Temps de réponse
   - Uptime système
   - Trafic réseau (octets entrants/sortants)
   - Erreurs réseau (erreurs entrantes/sortantes)
   - État opérationnel des interfaces
3. **Stockage** : Les métriques sont enregistrées dans la base de données PostgreSQL
4. **Historique** : Conservation complète de l'historique pour analyses et graphiques

### Dashboard de monitoring

Accédez au dashboard web interactif sur http://localhost:8000/monitoring/dashboard

Le dashboard offre une visualisation complète avec :

**Graphiques interactifs (Chart.js)** :
- Graphique en camembert : répartition UP/DOWN/UNKNOWN
- Graphique en barres : disponibilité 24h par routeur (code couleur : vert >= 99%, jaune >= 95%, rouge < 95%)
- Graphique en ligne : temps de réponse de chaque routeur

**Métriques globales** :
- Nombre total de routeurs
- Routeurs UP vs DOWN
- Disponibilité moyenne sur 24h

**Cartes détaillées par routeur** :
- État en temps réel (UP/DOWN/UNKNOWN)
- Disponibilité sur 24h avec code couleur
- Temps de réponse actuel
- Uptime système (jours et heures)
- Timestamp du dernier check

**Fonctionnalités** :
- Auto-refresh automatique toutes les 60 secondes
- Interface responsive (Bootstrap 5)
- Pas d'authentification requise

### Exemples de requêtes

**Obtenir les métriques des dernières 24 heures :**
```bash
curl "http://localhost:8000/monitoring/routers/1/metrics?hours=24&limit=100"
```

**Calculer la disponibilité sur une semaine :**
```bash
curl "http://localhost:8000/monitoring/routers/1/availability?hours=168"
```

**Obtenir les statistiques de bande passante :**
```bash
curl "http://localhost:8000/monitoring/routers/1/bandwidth?hours=24"
```

## Structure du projet

```
TD-FASTAPI/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py              # Configuration de la base de données
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py                 # Énumérations (types d'équipements, etc.)
│   │   ├── equipement.py            # Modèle de base pour les équipements
│   │   ├── ordinateur.py            # Modèle Ordinateur (hérite d'Equipement)
│   │   ├── router.py                # Modèle Router (hérite d'Equipement)
│   │   ├── ssh_connection.py        # Modèle pour les connexions SSH
│   │   └── snmp_metric.py           # Modèle pour les métriques SNMP
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ordinateurs.py           # Endpoints pour les ordinateurs
│   │   ├── routers.py               # Endpoints pour les routeurs
│   │   ├── equipements.py           # Endpoints génériques équipements
│   │   └── snmp_monitoring.py       # Endpoints monitoring SNMP
│   ├── services/
│   │   └── snmp_monitor.py          # Service de monitoring SNMP (tâche de fond)
│   ├── templates/
│   │   └── dashboard.html           # Template HTML du dashboard
│   └── main.py                      # Point d'entrée de l'application
├── config/
│   ├── snmpd.conf                   # Configuration SNMP pour le routeur
│   └── chrony.conf                  # Configuration NTP pour le routeur
├── frr-config/
│   ├── frr.conf                     # Configuration FRRouting (BGP, OSPF)
│   └── vtysh.conf                   # Configuration VTY shell
├── bruno/                           # Collection d'API testing (alternative à Postman)
├── requirements.txt                 # Dépendances Python
├── docker-compose.yml               # Orchestration des services
├── Dockerfile                       # Image Docker pour l'API FastAPI
├── Dockerfile.router                # Image Docker personnalisée pour le routeur FRR
└── README.md                        # Documentation du projet
```

## Technologies utilisées

| Catégorie | Technologies |
|-----------|--------------|
| **Framework Web** | FastAPI 0.115.0, Uvicorn (serveur ASGI) |
| **Base de données** | PostgreSQL 16, SQLModel, psycopg2 |
| **Connexion SSH** | Paramiko 3.4.0 |
| **Monitoring SNMP** | easysnmp 0.2.6 |
| **Templates** | Jinja2 3.1.2 |
| **Validation** | Pydantic 2.9.0 |
| **Conteneurisation** | Docker, Docker Compose |
| **Routeur** | FRRouting (FRR) - BGP, OSPF, RIP |

## Environnement de test

L'environnement de test complet est déployé via Docker Compose et comprend :

### Architecture de test

```
┌─────────────────────────────────────────────────┐
│           Réseau Docker: 172.230.0.0/24         │
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

### Services déployés

1. **database (PostgreSQL 16)**
   - IP: 172.230.0.2
   - Base de données pour stocker les équipements et métriques

2. **fastapi-app**
   - IP: 172.230.0.3
   - Port: 8000 (exposé sur l'hôte)
   - L'application FastAPI principale

3. **test-server-1 & test-server-2**
   - IPs: 172.230.0.10 et 172.230.0.11
   - Serveurs Python avec SSH activé
   - Credentials: root / testpass123
   - Utilisés pour tester le monitoring d'ordinateurs

4. **router (FRRouting)**
   - IP: 172.230.0.20
   - Image personnalisée avec FRR, SNMP, et NTP
   - Protocols: BGP, OSPF, RIP
   - SNMP v2c activé (community: public)
   - Credentials SSH: root / testpass123

### Commandes utiles

```bash
# Démarrer l'environnement complet
docker compose up -d

# Voir les logs de l'API
docker compose logs -f fastapi-app

# Accéder au routeur en SSH
docker exec -it router vtysh

# Redémarrer un service
docker compose restart fastapi-app

# Arrêter tout
docker compose down
```

## Problèmes rencontrés 
> Ici une liste des problèmes rencontrés lors du développement de l'application suivis de la manière avec laquelle je l'ai résolu

### 1. Suppression de routeurs avec métriques SNMP

**Problème** : Lors de l'ajout du monitoring SNMP, la suppression de routeurs échouait à cause de la relation de clé étrangère entre les tables `routers` et `snmp_metrics`.

**Solution** : Ajout d'une cascade de suppression dans le modèle SQLModel pour nettoyer automatiquement toutes les métriques associées avant de supprimer un routeur.

```python
# Dans app/models/snmp_metric.py
router_id: int = Field(foreign_key="router.id", ondelete="CASCADE")
```

### 2. Image Docker FRRouting obsolète

**Problème** : L'image officielle `frrouting/frr:latest` ne fonctionnait pas correctement et n'était plus maintenue depuis 2 ans.

**Solution** : Création d'une image Docker personnalisée ([Dockerfile.router](Dockerfile.router)) basée sur Ubuntu avec :
- Installation manuelle de FRRouting depuis les dépôts officiels
- Configuration de SNMP avec snmpd
- Configuration de NTP avec chrony
- Configuration SSH sécurisée

### 3. Permissions des fichiers de configuration montés

**Problème** : Le conteneur exécutait un `chown` sur les fichiers de configuration montés, rendant impossible leur modification depuis l'utilisateur local.

**Solution** :
- Utilisation de volumes nommés pour les données persistantes
- Les fichiers de configuration sont copiés au lieu d'être montés directement
- Alternative : ajustement des permissions avec l'option `:ro` (read-only) pour les configs

## Documentation interactive

Une fois l'application lancée, accédez à la documentation interactive :

- **Swagger UI** : http://localhost:8000/docs
  - Interface interactive pour tester tous les endpoints
  - Schémas de requêtes/réponses détaillés

- **Dashboard SNMP** : http://localhost:8000/monitoring/dashboard
  - Interface web de monitoring en temps réel avec graphiques interactifs
  - 3 graphiques Chart.js (camembert, barres, ligne)
  - Vue d'ensemble de tous les routeurs avec métriques détaillées
  - Auto-refresh toutes les 60 secondes
  - Responsive et accessible sans authentification


## Licence

Ce projet est développé dans un cadre éducatif.

## Auteur

**aguacero7**
- GitHub: [@aguacero7](https://github.com/aguacero7)
- Repository: [SysMonAPI](https://github.com/aguacero7/SysMonAPI)

## Liens utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [FRRouting Documentation](https://docs.frrouting.org)
- [SNMP Protocol](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
