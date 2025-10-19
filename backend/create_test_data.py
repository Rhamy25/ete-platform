#!/usr/bin/env python3
"""
Script pour créer des données de test pour l'application ETE
"""
import os
import sys
import django
from datetime import date, time

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')
django.setup()

from clients.models import ZoneCollecte, Client
from agents.models import Agent, Equipe, Vehicule
from collectes.models import Tournee

def create_test_data():
    """Créer des données de test"""
    
    print("🚀 Création des données de test...")
    
    # 1. Créer des zones de collecte
    zones_data = [
        {
            'nom': 'Centre-ville',
            'code': 'CV001',
            'description': 'Zone du centre-ville de Ouagadougou',
            'couleur_carte': '#3B82F6'
        },
        {
            'nom': 'Dassasgho',
            'code': 'DS001', 
            'description': 'Quartier Dassasgho',
            'couleur_carte': '#10B981'
        },
        {
            'nom': 'Tampouy',
            'code': 'TP001',
            'description': 'Secteur Tampouy',
            'couleur_carte': '#F59E0B'
        }
    ]
    
    zones = []
    for zone_data in zones_data:
        zone, created = ZoneCollecte.objects.get_or_create(
            nom_zone=zone_data['nom'],
            defaults={
                'code_zone': zone_data['code'],
                'description': zone_data['description'],
                'couleur': zone_data['couleur_carte'],
                'coordonnees_zone': []
            }
        )
        zones.append(zone)
        if created:
            print(f"✅ Zone créée: {zone.nom_zone}")
        else:
            print(f"⚠️  Zone existe déjà: {zone.nom_zone}")
    
    # 2. Créer des équipes
    equipes_data = [
        {
            'nom': 'Équipe Alpha',
            'code': 'EQ001',
            'chef_equipe': None,
            'statut': 'active'
        },
        {
            'nom': 'Équipe Beta',
            'code': 'EQ002', 
            'chef_equipe': None,
            'statut': 'active'
        },
        {
            'nom': 'Équipe Gamma',
            'code': 'EQ003',
            'chef_equipe': None,
            'statut': 'active'
        }
    ]
    
    equipes = []
    for equipe_data in equipes_data:
        equipe, created = Equipe.objects.get_or_create(
            nom=equipe_data['nom'],
            defaults=equipe_data
        )
        equipes.append(equipe)
        if created:
            print(f"✅ Équipe créée: {equipe.nom}")
        else:
            print(f"⚠️  Équipe existe déjà: {equipe.nom}")
    
    # 3. Créer des véhicules
    vehicules_data = [
        {
            'immatriculation': 'BF-123-ABC',
            'type_vehicule': 'camion_benne',
            'marque': 'Iveco',
            'modele': 'Daily',
            'annee': 2020,
            'capacite_charge': 3500.00,
            'statut': 'disponible'
        },
        {
            'immatriculation': 'BF-456-DEF',
            'type_vehicule': 'camion_benne',
            'marque': 'Mercedes',
            'modele': 'Sprinter',
            'annee': 2019,
            'capacite_charge': 2800.00,
            'statut': 'disponible'
        },
        {
            'immatriculation': 'BF-789-GHI',
            'type_vehicule': 'tricycle',
            'marque': 'Bajaj',
            'modele': 'RE 200',
            'annee': 2021,
            'capacite_charge': 500.00,
            'statut': 'disponible'
        }
    ]
    
    vehicules = []
    for vehicule_data in vehicules_data:
        vehicule, created = Vehicule.objects.get_or_create(
            immatriculation=vehicule_data['immatriculation'],
            defaults=vehicule_data
        )
        vehicules.append(vehicule)
        if created:
            print(f"✅ Véhicule créé: {vehicule.immatriculation}")
        else:
            print(f"⚠️  Véhicule existe déjà: {vehicule.immatriculation}")
    
    # 4. Créer des tournées
    tournees_data = [
        {
            'nom_tournee': 'Tournée Matinale Centre-ville',
            'date_tournee': date.today(),
            'heure_debut_prevue': time(8, 0),
            'heure_fin_prevue': time(12, 0),
            'equipe_assignee': equipes[0],
            'vehicule_assigne': vehicules[0],
            'zone_collecte': zones[0],
            'status': 'planifiee',
            'nombre_clients_prevus': 25,
            'nombre_clients_realises': 0
        },
        {
            'nom_tournee': 'Tournée Après-midi Dassasgho',
            'date_tournee': date.today(),
            'heure_debut_prevue': time(14, 0),
            'heure_fin_prevue': time(18, 0),
            'equipe_assignee': equipes[1],
            'vehicule_assigne': vehicules[1],
            'zone_collecte': zones[1],
            'status': 'en_cours',
            'nombre_clients_prevus': 30,
            'nombre_clients_realises': 12
        },
        {
            'nom_tournee': 'Tournée Matinale Tampouy',
            'date_tournee': date.today(),
            'heure_debut_prevue': time(7, 0),
            'heure_fin_prevue': time(11, 0),
            'equipe_assignee': equipes[2],
            'vehicule_assigne': vehicules[2],
            'zone_collecte': zones[2],
            'status': 'terminee',
            'nombre_clients_prevus': 18,
            'nombre_clients_realises': 18
        }
    ]
    
    tournees = []
    for tournee_data in tournees_data:
        tournee, created = Tournee.objects.get_or_create(
            nom_tournee=tournee_data['nom_tournee'],
            date_tournee=tournee_data['date_tournee'],
            defaults=tournee_data
        )
        tournees.append(tournee)
        if created:
            print(f"✅ Tournée créée: {tournee.nom_tournee}")
        else:
            print(f"⚠️  Tournée existe déjà: {tournee.nom_tournee}")
    
    print("\n🎉 Données de test créées avec succès!")
    print(f"📊 Résumé:")
    print(f"   - {len(zones)} zones de collecte")
    print(f"   - {len(equipes)} équipes")
    print(f"   - {len(vehicules)} véhicules")
    print(f"   - {len(tournees)} tournées")

if __name__ == "__main__":
    create_test_data()