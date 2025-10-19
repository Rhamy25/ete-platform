#!/usr/bin/env python3
"""Script pour créer des données de test pour ETE"""

import os
import sys
import django
from datetime import date, time, timedelta
from django.utils import timezone

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')
django.setup()

# Imports des modèles
from clients.models import ZoneCollecte, Client
from agents.models import Agent, Vehicule, Equipe
from collectes.models import Tournee, Collecte
from accounts.models import CustomUser

def create_test_data():
    print("🚀 Création des données de test ETE...")
    
    # 1. Créer des zones de collecte
    print("\n📍 Création des zones...")
    zones_data = [
        {
            'nom_zone': 'Centre-ville',
            'code_zone': 'CTR',
            'description': 'Zone du centre-ville de Ouagadougou',
            'couleur': '#1e3a8a',
            'coordonnees_zone': []
        },
        {
            'nom_zone': 'Secteur 1',
            'code_zone': 'S01',
            'description': 'Secteur 1 - Zone résidentielle',
            'couleur': '#dc2626',
            'coordonnees_zone': []
        },
        {
            'nom_zone': 'Secteur 15',
            'code_zone': 'S15',
            'description': 'Secteur 15 - Zone mixte',
            'couleur': '#059669',
            'coordonnees_zone': []
        },
        {
            'nom_zone': 'Zone Industrielle',
            'code_zone': 'ZI',
            'description': 'Zone industrielle de Kossodo',
            'couleur': '#d97706',
            'coordonnees_zone': []
        }
    ]
    
    zones = []
    for zone_data in zones_data:
        zone, created = ZoneCollecte.objects.get_or_create(
            code_zone=zone_data['code_zone'],
            defaults=zone_data
        )
        zones.append(zone)
        if created:
            print(f"✅ Zone créée: {zone.nom_zone}")
        else:
            print(f"⚠️  Zone existe déjà: {zone.nom_zone}")
    
    # 2. Créer des véhicules
    print("\n🚛 Création des véhicules...")
    vehicules_data = [
        {
            'numero_plaque': 'BF-123-ABC',
            'marque': 'Iveco',
            'modele': 'Daily',
            'annee': 2020,
            'type_vehicule': 'camion_benne',
            'capacite_charge': 3500.00,
            'capacite_volume': 15.00,
            'status': 'operationnel'
        },
        {
            'numero_plaque': 'BF-456-DEF',
            'marque': 'Mercedes',
            'modele': 'Atego',
            'annee': 2019,
            'type_vehicule': 'camion_compacteur',
            'capacite_charge': 5000.00,
            'capacite_volume': 20.00,
            'status': 'operationnel'
        },
        {
            'numero_plaque': 'BF-789-GHI',
            'marque': 'Ford',
            'modele': 'Transit',
            'annee': 2021,
            'type_vehicule': 'camionnette',
            'capacite_charge': 1500.00,
            'capacite_volume': 8.00,
            'status': 'operationnel'
        }
    ]
    
    vehicules = []
    for vehicule_data in vehicules_data:
        vehicule, created = Vehicule.objects.get_or_create(
            numero_plaque=vehicule_data['numero_plaque'],
            defaults=vehicule_data
        )
        vehicules.append(vehicule)
        if created:
            print(f"✅ Véhicule créé: {vehicule.numero_plaque} ({vehicule.marque} {vehicule.modele})")
        else:
            print(f"⚠️  Véhicule existe déjà: {vehicule.numero_plaque}")
    
    # 3. Créer des équipes
    print("\n👥 Création des équipes...")
    equipes_data = [
        {
            'nom_equipe': 'Équipe Alpha',
            'heure_debut': time(6, 0),
            'heure_fin': time(14, 0),
            'jours_travail': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi'],
            'is_active': True
        },
        {
            'nom_equipe': 'Équipe Beta',
            'heure_debut': time(7, 0),
            'heure_fin': time(15, 0),
            'jours_travail': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'],
            'is_active': True
        },
        {
            'nom_equipe': 'Équipe Gamma',
            'heure_debut': time(8, 0),
            'heure_fin': time(16, 0),
            'jours_travail': ['mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'],
            'is_active': True
        }
    ]
    
    equipes = []
    for equipe_data in equipes_data:
        equipe, created = Equipe.objects.get_or_create(
            nom_equipe=equipe_data['nom_equipe'],
            defaults=equipe_data
        )
        equipes.append(equipe)
        if created:
            print(f"✅ Équipe créée: {equipe.nom_equipe}")
            # Assigner des zones aux équipes
            if len(zones) > 0:
                equipe.zones_intervention.add(zones[len(equipes) % len(zones)])
        else:
            print(f"⚠️  Équipe existe déjà: {equipe.nom_equipe}")
    
    # 4. Créer des clients de test
    print("\n👥 Création des clients...")
    clients_data = [
        {
            'user_data': {
                'username': 'amadou.ouedraogo',
                'first_name': 'Amadou',
                'last_name': 'Ouedraogo',
                'email': 'amadou.ouedraogo@email.bf',
                'phone': '+226 70 12 34 56',
                'user_type': 'client'
            },
            'client_data': {
                'type_client': 'particulier',
                'status': 'actif',
                'service_address': 'Secteur 1, Rue 12.34',
                'service_city': 'Ouagadougou',
                'service_postal_code': '01000',
                'latitude': 12.3714,
                'longitude': -1.5197,
                'zone_key': 'secteur1'
            }
        },
        {
            'user_data': {
                'username': 'salimata.kabore',
                'first_name': 'Salimata',
                'last_name': 'Kaboré',
                'email': 'salimata.kabore@email.bf',
                'phone': '+226 70 23 45 67',
                'user_type': 'client'
            },
            'client_data': {
                'type_client': 'particulier',
                'status': 'actif',
                'service_address': 'Secteur 15, Avenue Yennenga',
                'service_city': 'Ouagadougou',
                'service_postal_code': '15000',
                'latitude': 12.3583,
                'longitude': -1.5355,
                'zone_key': 'secteur15'
            }
        },
        {
            'user_data': {
                'username': 'ibrahim.sawadogo',
                'first_name': 'Ibrahim',
                'last_name': 'Sawadogo',
                'email': 'ibrahim.sawadogo@email.bf',
                'phone': '+226 70 34 56 78',
                'user_type': 'client'
            },
            'client_data': {
                'type_client': 'entreprise',
                'status': 'actif',
                'company_name': 'Entreprise Sawadogo SARL',
                'contact_person': 'Ibrahim Sawadogo',
                'service_address': 'Zone industrielle de Kossodo, Lot 45',
                'service_city': 'Ouagadougou',
                'service_postal_code': 'ZI001',
                'latitude': 12.4167,
                'longitude': -1.4833,
                'zone_key': 'industrielle'
            }
        },
        {
            'user_data': {
                'username': 'fatimata.compaore',
                'first_name': 'Fatimata',
                'last_name': 'Compaoré',
                'email': 'fatimata.compaore@email.bf',
                'phone': '+226 70 45 67 89',
                'user_type': 'client'
            },
            'client_data': {
                'type_client': 'particulier',
                'status': 'actif',
                'service_address': 'Centre-ville, Avenue Kwamé Nkrumah',
                'service_city': 'Ouagadougou',
                'service_postal_code': '00001',
                'latitude': 12.3686,
                'longitude': -1.5275,
                'zone_key': 'centre'
            }
        },
        {
            'user_data': {
                'username': 'boukary.traore',
                'first_name': 'Boukary',
                'last_name': 'Traoré',
                'email': 'boukary.traore@email.bf',
                'phone': '+226 70 56 78 90',
                'user_type': 'client'
            },
            'client_data': {
                'type_client': 'particulier',
                'status': 'inactif',
                'service_address': 'Secteur 30, Rue 30.15 - Ouaga 2000',
                'service_city': 'Ouagadougou',
                'service_postal_code': '30000',
                'latitude': 12.3456,
                'longitude': -1.5123,
                'zone_key': 'secteur15'
            }
        }
    ]
    
    # Mapping des zones
    zone_mapping = {
        'centre': zones[0],      # Centre-ville
        'secteur1': zones[1],    # Secteur 1
        'secteur15': zones[2],   # Secteur 15
        'industrielle': zones[3] # Zone Industrielle
    }
    
    clients = []
    for i, data in enumerate(clients_data):
        user_info = data['user_data']
        client_info = data['client_data']
        
        # Créer ou récupérer l'utilisateur
        user, user_created = CustomUser.objects.get_or_create(
            username=user_info['username'],
            defaults=user_info
        )
        
        if user_created:
            user.set_password('password123')  # Mot de passe par défaut
            user.save()
        
        # Assigner la zone
        zone = zone_mapping.get(client_info['zone_key'], zones[0])
        client_info['zone_collecte'] = zone
        del client_info['zone_key']
        
        # Générer un code client unique
        client_info['code_client'] = f'CLT{i+1:04d}'
        
        # Créer ou récupérer le client
        try:
            client = Client.objects.get(user=user)
            created = False
            print(f"⚠️  Client existe déjà: {user.first_name} {user.last_name}")
        except Client.DoesNotExist:
            client = Client.objects.create(user=user, **client_info)
            created = True
            print(f"✅ Client créé: {user.first_name} {user.last_name} ({zone.nom_zone})")
        
        clients.append(client)
    
    # 5. Créer des agents de test
    print("\n👷 Création des agents...")
    agents_data = [
        {
            'user_data': {
                'username': 'agent.ramassage1',
                'first_name': 'Moussa',
                'last_name': 'Sankara',
                'email': 'moussa.sankara@ete.bf',
                'phone': '+226 70 11 22 33',
                'user_type': 'agent_ramassage'
            },
            'agent_data': {
                'poste': 'collecteur',
                'status': 'actif',
                'matricule': 'AGT001',
                'date_embauche': timezone.now().date(),
                'salaire_base': 85000.00
            }
        },
        {
            'user_data': {
                'username': 'agent.collecte1',
                'first_name': 'Aminata',
                'last_name': 'Zongo',
                'email': 'aminata.zongo@ete.bf',
                'phone': '+226 70 22 33 44',
                'user_type': 'agent_collecte'
            },
            'agent_data': {
                'poste': 'collecteur',
                'status': 'actif',
                'matricule': 'AGT002',
                'date_embauche': timezone.now().date(),
                'salaire_base': 90000.00
            }
        },
        {
            'user_data': {
                'username': 'agent.supervision1',
                'first_name': 'Ousmane',
                'last_name': 'Badolo',
                'email': 'ousmane.badolo@ete.bf',
                'phone': '+226 70 33 44 55',
                'user_type': 'agent_supervision'
            },
            'agent_data': {
                'poste': 'chef_equipe',
                'status': 'actif',
                'matricule': 'AGT003',
                'date_embauche': timezone.now().date(),
                'salaire_base': 120000.00
            }
        }
    ]
    
    agents = []
    for i, data in enumerate(agents_data):
        user_info = data['user_data']
        agent_info = data['agent_data']
        
        # Créer ou récupérer l'utilisateur
        user, user_created = CustomUser.objects.get_or_create(
            username=user_info['username'],
            defaults=user_info
        )
        
        if user_created:
            user.set_password('password123')
            user.save()
        
        # Créer ou récupérer l'agent
        try:
            agent = Agent.objects.get(user=user)
            created = False
            print(f"⚠️  Agent existe déjà: {user.first_name} {user.last_name}")
        except Agent.DoesNotExist:
            agent = Agent.objects.create(user=user, **agent_info)
            created = True
            print(f"✅ Agent créé: {user.first_name} {user.last_name} ({agent.poste})")
        
        agents.append(agent)

    # 6. Créer des tournées
    print("\n🗓️ Création des tournées...")
    today = timezone.now().date()
    
    for i in range(5):  # Créer 5 tournées
        tournee_date = today + timedelta(days=i)
        equipe = equipes[i % len(equipes)]
        vehicule = vehicules[i % len(vehicules)]
        zone = zones[i % len(zones)]
        
        tournee_data = {
            'nom_tournee': f'Tournée {zone.nom_zone} - {tournee_date.strftime("%d/%m")}',
            'date_tournee': tournee_date,
            'heure_debut_prevue': time(7, 0),
            'heure_fin_prevue': time(15, 0),
            'equipe_assignee': equipe,
            'vehicule_assigne': vehicule,
            'zone_collecte': zone,
            'nombre_clients_prevus': 25 + (i * 5),
            'nombre_clients_realises': 0 if i > 0 else 20,  # Première tournée partiellement réalisée
            'status': 'terminee' if i == 0 else 'planifiee' if i < 3 else 'en_cours'
        }
        
        tournee, created = Tournee.objects.get_or_create(
            nom_tournee=tournee_data['nom_tournee'],
            defaults=tournee_data
        )
        
        if created:
            print(f"✅ Tournée créée: {tournee.nom_tournee} ({tournee.status})")
        else:
            print(f"⚠️  Tournée existe déjà: {tournee.nom_tournee}")
    
    print("\n✅ Données de test créées avec succès !")
    print(f"📊 Résumé:")
    print(f"   - {ZoneCollecte.objects.count()} zones de collecte")
    print(f"   - {Vehicule.objects.count()} véhicules")
    print(f"   - {Equipe.objects.count()} équipes")
    print(f"   - {Agent.objects.count()} agents")
    print(f"   - {Client.objects.count()} clients")
    print(f"   - {Tournee.objects.count()} tournées")
    
    return True

if __name__ == '__main__':
    try:
        create_test_data()
        print("\n🎉 Script terminé avec succès !")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)