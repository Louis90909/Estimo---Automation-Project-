Estimo — Simulation immobilière et pipeline d’automatisation de données

1. Contexte et vision

Estimo est un projet de simulation immobilière visant à rendre l’estimation de la valeur des biens plus transparente, accessible et fondée sur la donnée publique.
Il s’agit d’une infrastructure de data engineering complète, permettant de collecter, traiter, stocker et exposer des données immobilières à travers une architecture entièrement automatisée et containerisée.

Le projet démontre la capacité à :
	•	orchestrer des traitements de données avec Apache Airflow ;
	•	assurer la persistance et la qualité via PostgreSQL ;
	•	superviser le pipeline avec Grafana et Prometheus ;
	•	exécuter l’ensemble dans un environnement Dockerisé et déployable sur Kubernetes.

⸻

2. Objectif général

Construire une plateforme unifiée pour :
	1.	Ingestion et agrégation des données publiques immobilières (DVF, indicateurs communaux).
	2.	Simulation et estimation du prix d’un bien via un formulaire utilisateur.
	3.	Automatisation des traitements et mises à jour quotidiennes.
	4.	Suivi de la qualité et de la performance via des outils open-source.

L’approche met l’accent sur la reproductibilité, la transparence et la robustesse du pipeline.

⸻

3. Problématique

Les plateformes d’estimation immobilière existantes sont souvent :
	•	opaques dans leurs calculs,
	•	basées sur des données non ouvertes,
	•	et rarement automatisées.

Estimo vise à démontrer qu’un modèle d’estimation fiable peut être produit à partir de données publiques, entièrement auditées, et automatisées de bout en bout.

⸻

4. Données et périmètre

4.1. Sources de données utilisées
	•	DVF (Demandes de Valeurs Foncières) : base nationale des transactions immobilières (prix, surface, nature, localisation).
	•	Indicateurs communaux (Boris Mericskay) : agrégats statistiques 2014–2024 par commune (prix moyen, volumes, répartition maison/appartement).
	•	Entrées utilisateur (Estimation Input) : formulaires saisis via le front-end.
	•	Schéma de qualité et de suivi (QA) : tables de contrôle interne des exécutions et de la fraîcheur des données.

4.2. Objectif fonctionnel

Le pipeline combine ces sources pour :
	•	produire une table de référence marché (par commune et année),
	•	permettre une jointure directe avec les saisies utilisateur,
	•	et générer une estimation baseline :
estimation = surface × prix_m2_moyen(commune).

⸻

5. Architecture conceptuelle

5.1. Vue d’ensemble

L’architecture Estimo repose sur six composants interconnectés :
| **Domaine** | **Technologie** | **Rôle principal** |
| --- | --- | --- |
| Frontend | HTML/CSS/JS + Nginx | Collecte des entrées utilisateur |
| API Backend | FastAPI (Python) | Traitement et calcul des estimations |
| Base de données | PostgreSQL | Stockage des données DVF, marché et utilisateurs |
| Orchestration | Apache Airflow | Automatisation des processus ETL |
| Monitoring | Prometheus + Grafana | Supervision technique et métier |
| Conteneurisation | Docker / Kubernetes | Déploiement reproductible et scalable |

6. Modèle de données

La base PostgreSQL constitue le socle de l’infrastructure.
Elle est structurée autour d’un modèle en étoile (star schema) centré sur les estimations.

6.1. Tables principales

| **Table** | **Description** | **Type** |
| --- | --- | --- |
| estimation_input | Données saisies par l’utilisateur (zone, surface, DPE, etc.) | Fait |
| dvf_full_raw | Transactions immobilières réelles issues du jeu DVF | Source brute |
| communes_market_2024 | Agrégats de prix et volumes par commune pour 2024 | Dimension |
| communes_market_yearly | Évolution temporelle par commune (2014–2024) | Dimension |
| estimation_baseline | Vue de référence liant input ↔ marché communal | Vue analytique |

6.2. Tables de suivi et qualité
| **Table** | **Description** | **Rôle** |
| --- | --- | --- |
| qa.check_results | Résultats des contrôles qualité exécutés à chaque run Airflow | Monitoring |
| grafana_refresh | Suivi de l’actualisation des dashboards Grafana | Monitoring |

7. Orchestration et automatisation

Les tâches sont exécutées via des DAGs Airflow, chacun correspondant à un maillon du pipeline :
| **DAG** | **Fonction** |
| --- | --- |
| ingest_dvf_full | Ingestion et nettoyage des données brutes DVF |
| build_communes_market_2024 | Agrégation des indicateurs de marché |
| estimation_input_daily | Actualisation et contrôle qualité des entrées utilisateurs |
| quality_checks_2024 | Validation automatisée des indicateurs et seuils métier |

Chaque DAG écrit ses logs et états dans la base, assurant un suivi complet des exécutions.


⸻

8. Monitoring et consommation

8.1. DBeaver

Utilisé pour la consultation directe et la validation des tables SQL.

8.2. Grafana

Connecté à la base PostgreSQL et à Prometheus :
	•	Tableaux techniques : charge CPU, mémoire, disponibilité des conteneurs.
	•	Tableaux métiers : volumes d’estimations, cohérence des prix, qualité des données.

8.3. Airflow UI

Interface d’administration des DAGs, permettant de suivre les exécutions, logs et dépendances.

⸻

9. Principes techniques et bonnes pratiques
	•	Anonymisation des données utilisateurs : aucune PII stockée, seules les clés de zone (insee_commune ou zone_key) sont conservées.
	•	Indexation systématique pour accélérer les jointures et agrégations.
	•	Schéma QA isolé pour tous les contrôles de cohérence et indicateurs de qualité.
	•	Réplication possible via PostgreSQL dump ou connecteur Prometheus.

Annexe 
Data Pipeline 
<img width="4100" height="2296" alt="Data Pipeline" src="https://github.com/user-attachments/assets/1a88648b-26f0-4193-b7be-5b238cf7f4e0" />



Data Model
<img width="2659" height="5805" alt="Data Model" src="https://github.com/user-attachments/assets/af0ea8e6-35f0-4d14-b6d0-3fd5b623b455" />
