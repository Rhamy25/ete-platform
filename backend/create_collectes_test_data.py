#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta, time
from decimal import Decimal

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')

django.setup()

from clients.models import Client, ZoneCollecte
from agents.models import Agent, Equipe, Vehicule
from collectes.models import Tournee, Collecte

def create_collectes_test_data():
    print("Création des données de test pour les collectes...")
    
    # Récupérer les données existantes
    zones = list(ZoneCollecte.objects.all())
    equipes = list(Equipe.objects.all())
    vehicules = list(Vehicule.objects.all())
    clients = list(Client.objects.all())
    
    if not zones or not equipes or not vehicules:
        print("❌ Erreur: Il faut d'abord créer des zones, équipes et véhicules")
        return
    
    # Supprimer les tournées existantes
    Tournee.objects.all().delete()
    print("✅ Données existantes supprimées")
    
    # Données de tournées
    tournees_data = [
        {
            'nom': 'Tournée Matinale Zone Nord',
            'zone': 'Zone Nord',
            'equipe': 'Équipe Alpha',
            'vehicule': 'ETE001',
            'date_offset': -2,  # Il y a 2 jours
            'heure_debut': time(7, 0),
            'heure_fin': time(12, 0),
            'status': 'terminee',
            'clients_prevus': 15,
            'clients_realises': 14
        },
        {
            'nom': 'Tournée Après-midi Zone Centre',
            'zone': 'Zone Centre',
            'equipe': 'Équipe Beta',
            'vehicule': 'ETE002', 
            'date_offset': -1,  # Hier
            'heure_debut': time(13, 30),
            'heure_fin': time(18, 0),
            'status': 'terminee',
            'clients_prevus': 22,
            'clients_realises': 20
        },
        {
            'nom': 'Tournée du Matin Zone Sud',
            'zone': 'Zone Sud',
            'equipe': 'Équipe Gamma',
            'vehicule': 'ETE003',
            'date_offset': 0,  # Aujourd'hui
            'heure_debut': time(6, 30),
            'heure_fin': time(11, 30),
            'status': 'en_cours',
            'clients_prevus': 18,
            'clients_realises': 12
        },
        {
            'nom': 'Tournée Collecte Zone Est',
            'zone': 'Zone Est',
            'equipe': 'Équipe Alpha',
            'vehicule': 'ETE001',
            'date_offset': 0,  # Aujourd'hui
            'heure_debut': time(14, 0),
            'heure_fin': time(17, 30),
            'status': 'planifiee',
            'clients_prevus': 25,
            'clients_realises': 0
        },
        {
            'nom': 'Tournée Weekend Zone Ouest',
            'zone': 'Zone Ouest',
            'equipe': 'Équipe Delta',
            'vehicule': 'ETE004',
            'date_offset': 1,  # Demain
            'heure_debut': time(8, 0),
            'heure_fin': time(13, 0),
            'status': 'planifiee',
            'clients_prevus': 20,
            'clients_realises': 0
        },
        {
            'nom': 'Tournée Spéciale Zone Centre',
            'zone': 'Zone Centre',
            'equipe': 'Équipe Beta',
            'vehicule': 'ETE002',
            'date_offset': 2,  # Après-demain
            'heure_debut': time(9, 0),
            'heure_fin': time(15, 0),
            'status': 'planifiee',
            'clients_prevus': 30,
            'clients_realises': 0
        },
        {
            'nom': 'Tournée Annulée Zone Nord',
            'zone': 'Zone Nord',
            'equipe': 'Équipe Gamma',
            'vehicule': 'ETE003',
            'date_offset': -3,  # Il y a 3 jours
            'heure_debut': time(10, 0),
            'heure_fin': time(16, 0),
            'status': 'annulee',
            'clients_prevus': 12,
            'clients_realises': 0
        }
    ]
    
    # Créer les tournées
    tournees_creees = []
    for data in tournees_data:
        try:
            # Trouver la zone
            zone = next((z for z in zones if data['zone'] in z.nom_zone), zones[0])
            
            # Trouver l'équipe
            equipe = next((e for e in equipes if data['equipe'] in e.nom_equipe), equipes[0])
            
            # Trouver le véhicule
            vehicule = next((v for v in vehicules if data['vehicule'] in v.numero_plaque), vehicules[0])
            
            # Date de la tournée
            date_tournee = datetime.now().date() + timedelta(days=data['date_offset'])
            
            tournee = Tournee.objects.create(
                nom_tournee=data['nom'],
                date_tournee=date_tournee,
                heure_debut_prevue=data['heure_debut'],
                heure_fin_prevue=data['heure_fin'],
                equipe_assignee=equipe,
                vehicule_assigne=vehicule,
                zone_collecte=zone,
                status=data['status'],
                nombre_clients_prevus=data['clients_prevus'],
                nombre_clients_realises=data['clients_realises'],
                notes=f"Tournée {data['status']} pour la {data['zone']}",
                distance_parcourue=Decimal('25.5') if data['status'] == 'terminee' else None,
                carburant_consomme=Decimal('8.2') if data['status'] == 'terminee' else None
            )
            
            # Pour les tournées terminées ou en cours, ajouter les heures réelles
            if data['status'] in ['terminee', 'en_cours']:
                tournee.heure_debut_reelle = data['heure_debut']
                if data['status'] == 'terminee':
                    tournee.heure_fin_reelle = data['heure_fin']
                tournee.save()
            
            tournees_creees.append(tournee)
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la tournée {data['nom']}: {e}")
    
    print(f"✅ {len(tournees_creees)} tournées créées")
    
    # Créer quelques collectes individuelles pour les tournées
    collectes_creees = 0
    for tournee in tournees_creees[:3]:  # Pour les 3 premières tournées
        clients_zone = clients[:min(len(clients), tournee.nombre_clients_prevus)]
        
        for i, client in enumerate(clients_zone[:5]):  # Limiter à 5 collectes par tournée
            try:
                heure_passage = time(
                    tournee.heure_debut_prevue.hour + (i // 3),
                    (i * 20) % 60
                )
                
                status = 'completee' if tournee.status == 'terminee' else (
                    'en_cours' if i < tournee.nombre_clients_realises else 'planifiee'
                )
                
                collecte = Collecte.objects.create(
                    tournee=tournee,
                    client=client,
                    heure_passage_prevue=heure_passage,
                    ordre_passage=i + 1,
                    status=status,
                    types_dechets_collectes=['organiques', 'recyclables'],
                    quantite_estimee=Decimal('15.5') if status == 'completee' else None,
                    nombre_contenants=2,
                    notes_agent=f"Collecte {status} chez {client.user.get_full_name()}"
                )
                
                if status == 'completee':
                    collecte.heure_arrivee = heure_passage
                    collecte.heure_depart = time(
                        heure_passage.hour,
                        (heure_passage.minute + 15) % 60
                    )
                    collecte.save()
                
                collectes_creees += 1
                
            except Exception as e:
                print(f"❌ Erreur lors de la création de la collecte pour {client}: {e}")
    
    print(f"✅ {collectes_creees} collectes individuelles créées")
    
    # Statistiques finales
    print(f"\n📊 Statistiques des tournées créées:")
    print(f"   • Planifiées: {Tournee.objects.filter(status='planifiee').count()}")
    print(f"   • En cours: {Tournee.objects.filter(status='en_cours').count()}")
    print(f"   • Terminées: {Tournee.objects.filter(status='terminee').count()}")
    print(f"   • Annulées: {Tournee.objects.filter(status='annulee').count()}")
    print(f"   • Total collectes: {Collecte.objects.count()}")

if __name__ == '__main__':
    create_collectes_test_data()
    print("\n🎉 Données de test pour les collectes créées avec succès !")