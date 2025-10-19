<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created. ✅ Completed

- [x] Clarify Project Requirements ✅ Completed
	<!-- Projet: Plateforme web et mobile de gestion des ramassages d'ordures pour ETE. Stack: Python/Django REST API backend, React/Next.js frontend, React Native mobile. Base de données PostgreSQL/SQLite. -->

- [x] Scaffold the Project ✅ Completed
	<!-- 
	Structure créée: backend/ (Django + DRF), frontend/ (React), mobile/ (React Native), docs/
	Applications Django créées: accounts, clients, agents, collectes, paiements, notifications
	Configuration Django: settings.py mis à jour avec DRF, CORS, JWT, etc.
	Modèles créés: CustomUser, Client, Contrat, Agent, Vehicule, Equipe, ZoneCollecte
	-->

- [x] Customize the Project ✅ Completed
	<!--
	Modèles adaptés selon le cahier des charges:
	- Types d'utilisateurs: admin, agents (ramassage/collecte/prospection/supervision), clients, visiteurs
	- QR Codes pour validation des passages et paiements
	- Système de géolocalisation obligatoire pour agents
	- Gestion des bacs/poubelles multiples par client
	- Système de facturation automatique basé sur quantité
	- Paiements multiples: espèces, mobile money, MyPayBF, etc.
	- Règles de gestion: inactivité 3 mois, validation 48h, etc.
	- Demandes de prospection pour visiteurs
	- Sessions agents avec géolocalisation
	-->

- [x] Install Required Extensions ✅ Completed
	<!-- Aucune extension VS Code spécifique requise pour ce projet Django. -->

- [x] Compile the Project ✅ Completed
	<!--
	Dépendances installées: Django, DRF, JWT, QRCode, MySQL, etc.
	Migrations créées et appliquées avec succès
	Modèle CustomUser configuré comme AUTH_USER_MODEL
	Base de données SQLite créée et fonctionnelle
	Superutilisateur créé: admin@ete.com
	Serveur de développement démarré sur http://127.0.0.1:8000/
	-->

- [x] Create and Run Task ✅ Completed
	<!--
	API REST complète créée avec ViewSets et Serializers pour:
	- Accounts: Gestion utilisateurs, sessions agents, QR codes
	- Clients: CRUD clients, contrats, zones, bacs, demandes prospection
	- Agents: Gestion agents, véhicules, équipes, performances
	- URLs configurées avec routeurs DRF
	- Permissions et filtres selon cahier des charges
	-->

- [ ] Launch the Project
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [ ] Ensure Documentation is Complete
	<!--
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->