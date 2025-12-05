# Collection Bruno - API FastAPI

Cette collection Bruno contient toutes les requêtes pour tester l'API de surveillance des routeurs et ordinateurs.

## Configuration

### Environnement

L'environnement `fastapi-dev` est configuré avec les variables suivantes :

- `baseUrl`: http://localhost:8000
- `authToken`: (sera automatiquement rempli après le login)

### Démarrage rapide

1. **Créer un utilisateur** :
   - Exécutez la requête `Register User`
   - Utilisez les credentials par défaut ou modifiez-les dans le body

2. **Se connecter** :
   - Exécutez la requête `Login`
   - Le token JWT sera automatiquement stocké dans la variable `authToken`
   - Ce token sera utilisé automatiquement par toutes les requêtes protégées

3. **Tester l'authentification** :
   - Exécutez `Get Current User` pour vérifier que le token fonctionne

## Authentification

### Requêtes d'authentification

- **Register User** : Créer un nouveau compte utilisateur
- **Login** : Se connecter et obtenir un token JWT
- **Get Current User** : Récupérer les infos de l'utilisateur connecté

### Requêtes protégées

Les requêtes suivantes nécessitent un token JWT valide (authentification Bearer) :

#### Routers
- `add router` - POST /routers
- `edit router` - PUT /routers/{id}
- `delete router` - DELETE /routers/{id}

#### Ordinateurs
- `add ordinateur` - POST /ordinateurs
- `edit ordinateur` - PUT /ordinateurs/{id}
- `delete ordinateur` - DELETE /ordinateurs/{id}

### Requêtes publiques

Les requêtes GET ne nécessitent pas d'authentification :
- `get routers` - GET /routers
- `get ordinateurs` - GET /ordinateurs
- Toutes les requêtes de monitoring SNMP
- Tous les endpoints de consultation

## Workflow typique

1. **Inscription** (une seule fois)
   ```
   POST /auth/register
   {
     "username": "admin",
     "email": "admin@example.com",
     "password": "admin123"
   }
   ```

2. **Connexion** (au début de chaque session)
   ```
   POST /auth/login
   Form Data:
   - username: admin
   - password: admin123
   ```
   → Le token est automatiquement sauvegardé dans `authToken`

3. **Utiliser l'API**
   - Les requêtes protégées utilisent automatiquement `{{authToken}}`
   - Les requêtes publiques fonctionnent sans token

## Notes

- Le token JWT expire après **30 minutes**
- Si vous recevez une erreur 401, reconnectez-vous avec `Login`
- Le script post-response dans `Login` met à jour automatiquement le token
- Toutes les requêtes utilisent `{{baseUrl}}` pour faciliter le changement d'environnement

## Structure des dossiers

```
bruno/
├── environments/
│   └── fastapi-dev.bru          # Variables d'environnement
├── auth_register.bru            # Inscription
├── auth_login.bru               # Connexion
├── auth_me.bru                  # Info utilisateur
├── add_router.bru               # 🔒 Ajouter un routeur
├── edit_router.bru              # 🔒 Modifier un routeur
├── delete_router.bru            # 🔒 Supprimer un routeur
├── get_routers.bru              # Lister les routeurs
├── add ordinateur.bru           # 🔒 Ajouter un ordinateur
├── edit_ordinateur.bru          # 🔒 Modifier un ordinateur
├── delete_ordinateur.bru        # 🔒 Supprimer un ordinateur
├── get ordinateurs.bru          # Lister les ordinateurs
└── ... (autres requêtes)
```

🔒 = Requête protégée (nécessite authentification)
