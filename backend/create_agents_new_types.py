#!/usr/bin/env python
"""
Script pour créer des agents avec les nouveaux types
"""

import os
import sys
import django
from datetime import date

# Configuration Django
sys.path.append('C:/Users/rhasm/OneDrive/Bureau/ETE/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')
django.setup()

from accounts.models import CustomUser
from agents.models import Agent, Equipe, Vehicule
from clients.models import ZoneCollecte

def create_agents_with_new_types():
    """Créer des agents avec les nouveaux types"""
    
    print("🔄 Création d'agents avec les nouveaux types...")
    
    # Récupérer une zone par défaut
    zone = ZoneCollecte.objects.first()
    if not zone:
        print("❌ Aucune zone de collecte trouvée")
        return
    
    # Agents à créer
    agents_data = [
        {
            'username': 'collecteur_argent_01',
            'email': 'collecteur.argent@ete.bf',
            'first_name': 'Aminata',
            'last_name': 'KONE',
            'phone': '+226 70 11 22 33',
            'poste': 'collecteur_argent',
            'matricule': 'ETE-CA-001'
        },
        {
            'username': 'agent_prospection_01',
            'email': 'agent.prospection@ete.bf', 
            'first_name': 'Ibrahim',
            'last_name': 'SAWADOGO',
            'phone': '+226 70 44 55 66',
            'poste': 'agent_prospection',
            'matricule': 'ETE-AP-001'
        },
        {
            'username': 'chauffeur_01',
            'email': 'chauffeur@ete.bf',
            'first_name': 'Bakary',
            'last_name': 'TRAORE',
            'phone': '+226 70 77 88 99',
            'poste': 'chauffeur',
            'matricule': 'ETE-CH-001'
        }
    ]
    
    for agent_data in agents_data:
        # Créer l'utilisateur s'il n'existe pas
        user, created = CustomUser.objects.get_or_create(
            username=agent_data['username'],
            defaults={
                'email': agent_data['email'],
                'first_name': agent_data['first_name'],
                'last_name': agent_data['last_name'],
                'phone': agent_data['phone'],
                'user_type': 'agent_collecte',
                'is_staff': False,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('ete123')
            user.save()
            print(f"✅ Utilisateur créé: {user.get_full_name()}")
        
        # Créer l'agent s'il n'existe pas
        agent, agent_created = Agent.objects.get_or_create(
            matricule=agent_data['matricule'],
            defaults={
                'user': user,
                'poste': agent_data['poste'],
                'status': 'actif',
                'date_embauche': date.today(),
                'zone_principale': zone
            }
        )
        
        if agent_created:
            print(f"✅ Agent créé: {agent.matricule} - {agent.get_poste_display()}")
        else:
            print(f"ℹ️ Agent existant: {agent.matricule}")
    
    # Afficher la répartition finale
    print("\n📊 Répartition finale des types d'agents :")
    for poste_code, poste_name in Agent.POSTE_CHOICES:
        count = Agent.objects.filter(poste=poste_code).count()
        print(f"  - {poste_name}: {count} agent(s)")
    
    print(f"\n📈 Total: {Agent.objects.count()} agent(s)")
    print("\n✨ Création terminée !")

if __name__ == '__main__':
    create_agents_with_new_types()