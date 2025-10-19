#!/usr/bin/env python
"""
Script pour migrer les anciens types d'agents vers les nouveaux
"""

import os
import sys
import django

# Configuration Django
sys.path.append('C:/Users/rhasm/OneDrive/Bureau/ETE/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ete_project.settings')
django.setup()

from agents.models import Agent

def migrate_agent_types():
    """Migration des types d'agents"""
    
    # Mapping des anciens types vers les nouveaux
    type_mapping = {
        'collecteur': 'ramasseur_ordures',
        'chef_equipe': 'superviseur',  # ou 'agent_prospection' selon le contexte
    }
    
    print("🔄 Migration des types d'agents...")
    
    for old_type, new_type in type_mapping.items():
        agents_updated = Agent.objects.filter(poste=old_type).update(poste=new_type)
        if agents_updated > 0:
            print(f"✅ {agents_updated} agent(s) migré(s) de '{old_type}' vers '{new_type}'")
    
    # Affichage des types actuels
    print("\n📊 Répartition actuelle des types d'agents :")
    for poste_code, poste_name in Agent.POSTE_CHOICES:
        count = Agent.objects.filter(poste=poste_code).count()
        print(f"  - {poste_name}: {count} agent(s)")
    
    print("\n✨ Migration terminée !")

if __name__ == '__main__':
    migrate_agent_types()