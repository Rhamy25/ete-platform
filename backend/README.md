# ETE Backend - API REST

Backend Django pour la plateforme de gestion des ramassages d'ordures de l'entreprise ETE.

## 🚀 Technologies utilisées

- **Framework**: Django 5.2.7 + Django REST Framework
- **Base de données**: MySQL (SQLite en développement)
- **Authentification**: JWT + Djoser
- **Cartographie**: Support géolocalisation GPS
- **QR Codes**: Génération automatique pour clients
- **Tâches asynchrones**: Celery + Redis

## 📋 Fonctionnalités principales

### Gestion des utilisateurs
- **Administrateur ETE**: Gestion complète du système
- **Agents spécialisés**: 
  - Ramassage (validation QR code, géolocalisation)
  - Collecte d'argent (paiements, QR validation)
  - Prospection (nouveaux clients, contrats)
  - Supervision (suivi équipes, remarques)
- **Clients**: Consultation contrats, historiques, notifications
- **Visiteurs**: Demandes d'abonnement, informations

### Gestion des collectes
- Tournées planifiées avec géolocalisation
- Validation passages par QR code obligatoire
- Suivi temps réel des agents
- Gestion incidents et réclamations
- Photos et signatures numériques

### Gestion des paiements
- Multiples modes: espèces, mobile money, MyPayBF
- Validation QR code obligatoire pour agents
- Facturation automatique selon quantité
- Règle 48h validation client
- Génération reçus numériques/papier

### Règles de gestion
- Inactivité client: alerte après 3 mois sans paiement
- Géolocalisation obligatoire pour agents
- Sessions terrain avec tracking
- Validation croisée QR codes
- Notifications automatiques multi-niveaux

## 🛠️ Installation

### Prérequis
- Python 3.12+
- MySQL (ou SQLite pour développement)
- Redis (pour Celery)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Configuration
1. Copier `.env.example` vers `.env`
2. Configurer les variables d'environnement
3. Créer la base de données MySQL

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Démarrage
```bash
# Serveur de développement
python manage.py runserver

# Celery (tâches asynchrones)
celery -A ete_project worker -l info
```

## 📊 Structure des applications

### `accounts`
- Modèles utilisateurs personnalisés
- QR codes clients
- Sessions agents géolocalisées

### `clients` 
- Gestion clients et contrats
- Zones de collecte
- Bacs/poubelles multiples
- Demandes de prospection

### `agents`
- Agents spécialisés par métier
- Véhicules et équipes
- Affectations zones

### `collectes`
- Tournées planifiées
- Collectes individuelles avec QR
- Réclamations et incidents

### `paiements`
- Factures automatiques
- Paiements multi-modes
- Reçus et rapports
- Validation 48h

### `notifications`
- Notifications temps réel
- Alertes système
- Rapports automatiques

## 🔐 API Endpoints

### Authentification
- `POST /api/auth/token/` - Obtenir token JWT
- `POST /api/auth/token/refresh/` - Renouveler token
- `POST /api/auth/users/` - Créer utilisateur

### Clients
- `GET /api/clients/` - Liste clients
- `POST /api/clients/` - Créer client
- `GET /api/clients/{id}/qr-code/` - QR code client

### Collectes
- `GET /api/collectes/tournees/` - Tournées du jour
- `POST /api/collectes/valider-passage/` - Valider passage QR
- `POST /api/collectes/incidents/` - Signaler incident

### Paiements
- `POST /api/paiements/` - Enregistrer paiement
- `POST /api/paiements/valider-qr/` - Valider QR paiement
- `GET /api/paiements/rapports/` - Rapports agent

## 🗺️ Géolocalisation

Le système utilise intensivement la géolocalisation :
- **Sessions agents**: Connexion géolocalisée obligatoire
- **Collectes**: Position validée dans zone assignée
- **Paiements**: Localisation des transactions
- **Cartographie**: Affichage temps réel sur carte

## 📱 QR Codes

Système QR codes omniprésent :
- **Clients**: QR unique auto-généré
- **Passages**: Validation obligatoire par agents ramassage
- **Paiements**: Validation obligatoire par agents collecte
- **Sécurité**: Prévention fraudes et erreurs

## ⚡ Notifications

Système notifications multi-niveaux :
- **Clients**: Ramassage effectué, factures, incidents
- **Agents**: Modifications tournées, affectations, alertes
- **Administration**: Rapports quotidiens, incidents, inactivité

## 🔧 Configuration avancée

### Variables d'environnement (.env)
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
USE_SQLITE=True  # False pour MySQL

# MySQL (production)
DB_NAME=ete_db
DB_USER=username
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306

# Email notifications
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379
```

### Couleurs ETE
- **Primaire**: #1e3a8a (Bleu marine)  
- **Secondaire**: #166534 (Vert foncé)

## 📈 Monitoring

### Logs système
- Connexions agents géolocalisées
- Validations QR codes
- Paiements et contestations
- Incidents de collecte

### Métriques clés
- Taux de passage réalisé/prévu
- Temps moyen collecte par client
- Délais de paiement
- Satisfaction client

## 🚨 Sécurité

- Authentification JWT obligatoire
- Validation géolocalisation agents
- QR codes uniques anti-fraude
- Audit trail complet
- Sessions sécurisées

## 👥 Équipe de développement

Projet ETE - Plateforme de gestion des ramassages d'ordures
Backend API REST Django développé selon cahier des charges spécifique.