#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')

django.setup()

from clients.models import Client, Contrat, ZoneCollecte

def create_contrats_test_data():
    print("Création des contrats de test...")
    
    # Récupérer les clients sans contrat
    clients = Client.objects.filter(contrats__isnull=True)
    zones = list(ZoneCollecte.objects.all())
    
    if not clients.exists():
        print("❌ Tous les clients ont déjà des contrats ou aucun client trouvé")
        return
    
    if not zones:
        print("❌ Aucune zone de collecte trouvée")
        return
    
    print(f"📋 Création de contrats pour {clients.count()} clients...")
    
    # Types de service variés
    types_service = [
        ('collecte_standard', 'Collecte Standard', 15000),
        ('collecte_premium', 'Collecte Premium', 25000),
        ('collecte_entreprise', 'Collecte Entreprise', 35000),
    ]
    
    frequences = ['quotidien', 'bi_hebdomadaire', 'hebdomadaire']
    
    contrats_crees = 0
    for client in clients:
        try:
            # Choisir un type de service aléatoire
            type_service, libelle, tarif = random.choice(types_service)
            
            # Date de début (entre 6 mois et 1 an dans le passé)
            jours_debut = random.randint(180, 365)
            date_debut = datetime.now().date() - timedelta(days=jours_debut)
            
            # Date de fin (1 an après le début)
            date_fin = date_debut + timedelta(days=365)
            
            # Générer un numéro de contrat unique
            numero_contrat = f"CTR{datetime.now().year}{client.id:03d}{random.randint(10,99)}"
            
            contrat = Contrat.objects.create(
                client=client,
                numero_contrat=numero_contrat,
                date_debut=date_debut,
                date_fin=date_fin,
                frequence_collecte=random.choice(frequences),
                jours_collecte=['lundi', 'mercredi', 'vendredi'],  # Exemple de jours
                heure_passage=datetime.strptime('08:00', '%H:%M').time(),
                tarif_mensuel=Decimal(str(tarif)),
                devise='XOF',  # Franc CFA
                types_dechets=['menagers', 'recyclables'],
                status='actif' if random.random() > 0.1 else 'suspendu',  # 90% actifs
                conditions_particulieres=f"Contrat {type_service} pour {client.user.get_full_name()}"
            )
            
            contrats_crees += 1
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du contrat pour {client}: {e}")
    
    print(f"✅ {contrats_crees} contrats créés avec succès")
    
    # Statistiques
    print(f"\n📊 Statistiques des contrats:")
    print(f"   • Actifs: {Contrat.objects.filter(status='actif').count()}")
    print(f"   • Suspendus: {Contrat.objects.filter(status='suspendu').count()}")
    print(f"   • Total: {Contrat.objects.count()}")

if __name__ == '__main__':
    create_contrats_test_data()
    print("\n🎉 Contrats de test créés avec succès !")