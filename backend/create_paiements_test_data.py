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

from clients.models import Client
from paiements.models import Paiement, Facture

def create_paiements_test_data():
    print("Création des données de test pour les paiements...")
    
    # Récupérer les clients existants
    clients = list(Client.objects.all())
    
    if not clients:
        print("❌ Erreur: Il faut d'abord créer des clients")
        return
    
    # Supprimer les paiements existants
    Paiement.objects.all().delete()
    Facture.objects.all().delete()
    print("✅ Données existantes supprimées")
    
    # Créer quelques factures d'abord
    factures_creees = []
    for i, client in enumerate(clients[:10]):  # Pour les 10 premiers clients
        facture = Facture.objects.create(
            client=client,
            contrat=client.contrats.first() if client.contrats.exists() else None,
            periode_facturation='mensuel',
            date_debut_periode=datetime.now().date().replace(day=1),
            date_fin_periode=datetime.now().date(),
            montant_ht=Decimal('12000'),
            montant_ttc=Decimal('15000'),
            date_emission=datetime.now().date(),
            date_echeance=datetime.now().date() + timedelta(days=30),
            nombre_passages_prevu=8,
            nombre_passages_realise=random.randint(6, 8)
        )
        factures_creees.append(facture)
    
    print(f"✅ {len(factures_creees)} factures créées")
    
    # Données de paiements variés
    modes_paiement = ['espece', 'mobile_money', 'virement', 'cheque', 'mypay_bf']
    status_choices = ['valide', 'en_attente', 'refuse', 'en_verification']
    
    paiements_data = []
    
    # Paiements récents (7 derniers jours)
    for i in range(25):
        client = random.choice(clients)
        facture = random.choice(factures_creees) if factures_creees else None
        
        # Date aléatoire dans les 7 derniers jours
        jours_offset = random.randint(0, 7)
        date_paiement = datetime.now() - timedelta(days=jours_offset)
        
        # Montant basé sur la facture ou aléatoire
        montant = facture.montant_ttc if facture else Decimal(random.randint(8000, 25000))
        
        # Mode de paiement et statut
        mode = random.choice(modes_paiement)
        
        # Probabilité de validation plus élevée pour les anciens paiements
        if jours_offset > 2:
            status = random.choices(status_choices, weights=[70, 20, 5, 5])[0]
        else:
            status = random.choices(status_choices, weights=[40, 40, 10, 10])[0]
        
        paiement_data = {
            'facture': facture,
            'client': client,
            'montant': montant,
            'mode_paiement': mode,
            'status': status,
            'date_paiement': date_paiement,
            'reference_transaction': f"TXN{random.randint(100000, 999999)}" if mode in ['mobile_money', 'virement', 'mypay_bf'] else '',
            'numero_cheque': f"CHQ{random.randint(1000, 9999)}" if mode == 'cheque' else '',
            'notes': f"Paiement {mode} - {status}"
        }
        
        paiements_data.append(paiement_data)
    
    # Créer les paiements
    paiements_crees = []
    for data in paiements_data:
        try:
            paiement = Paiement.objects.create(**data)
            
            # Ajouter des coordonnées GPS pour les paiements en espèces
            if data['mode_paiement'] == 'espece':
                paiement.latitude_paiement = Decimal('12.3714') + (random.random() - 0.5) * 0.1
                paiement.longitude_paiement = Decimal('-1.5197') + (random.random() - 0.5) * 0.1
                paiement.save()
            
            # Marquer comme validé si le statut est valide
            if data['status'] == 'valide':
                paiement.date_validation = data['date_paiement'] + timedelta(hours=random.randint(1, 48))
                paiement.save()
            
            paiements_crees.append(paiement)
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du paiement: {e}")
    
    print(f"✅ {len(paiements_crees)} paiements créés")
    
    # Statistiques finales
    print(f"\n📊 Statistiques des paiements créés:")
    print(f"   • Validés: {Paiement.objects.filter(status='valide').count()}")
    print(f"   • En attente: {Paiement.objects.filter(status='en_attente').count()}")
    print(f"   • En vérification: {Paiement.objects.filter(status='en_verification').count()}")
    print(f"   • Refusés: {Paiement.objects.filter(status='refuse').count()}")
    
    # Montants par méthode
    print(f"\n💰 Montants par méthode de paiement:")
    for mode in modes_paiement:
        total = Paiement.objects.filter(
            mode_paiement=mode, 
            status='valide'
        ).aggregate(total=Sum('montant'))['total'] or 0
        print(f"   • {mode.replace('_', ' ').title()}: {total:,.0f} FCFA")
    
    # Total encaissé
    total_encaisse = Paiement.objects.filter(status='valide').aggregate(
        total=Sum('montant')
    )['total'] or 0
    print(f"\n🎯 Total encaissé: {total_encaisse:,.0f} FCFA")

if __name__ == '__main__':
    # Import nécessaire pour Sum
    from django.db.models import Sum
    
    create_paiements_test_data()
    print("\n🎉 Données de test pour les paiements créées avec succès !")