# Estimo---Automation-Project-

## 🎯 Objectif du projet
Ce projet vise à construire une **infrastructure de data automation & deployment** complète, basée sur une stack open-source et gratuite.  
L’objectif est de démontrer la capacité à :
- Dockeriser des services (API, Airflow, Monitoring),
- Automatiser les traitements avec Airflow,
- Monitorer les performances via Prometheus & Grafana,
- Et déployer l’ensemble sur Kubernetes.

---

## 📁 Arborescence du dépôt
frontend/              → Landing page ou interface utilisateur simple
api/                   → API Flask/FastAPI (accès aux données ou prédictions)
db/                    → Scripts SQL & jeux de données (CSV)
├─ sql/
└─ csv/
airflow/               → DAGs d’orchestration
├─ dags/
└─ plugins/
monitoring/            → Stack Prometheus + Grafana
├─ prometheus/
└─ grafana/
k8s/                   → Manifests Kubernetes (déploiement, services, monitoring)
docs/                  → Documentation, schémas, livrables & preuves
└─ img/

---

## 📦 Livrables attendus (périmètre jury)

| Livrable | Description | Preuve (DoD) |
|-----------|--------------|---------------|
| **Dockerisation complète** | Tous les composants (API, Airflow, Prometheus, Grafana) sont containerisés et exécutables ensemble. | `docker-compose.yml` + captures des conteneurs en cours d’exécution. |
| **Orchestration Airflow** | Un DAG fonctionnel planifie et exécute les tâches d’ingestion ou de traitement. | Capture de l’interface Airflow avec le DAG en “success”. |
| **Monitoring Grafana** | Dashboards connectés à Prometheus pour suivre les métriques système et applicatives. | Capture d’écran d’un dashboard Grafana opérationnel. |
| **Déploiement Kubernetes** | Manifests et ressources pour exécuter les services dans un cluster (minikube, kind ou autre). | Fichiers `.yaml` + preuve de `kubectl get pods`. |
| **Benchmarks** | Évaluation de la performance et de la scalabilité (temps d’exécution, CPU/RAM, latence). | Tableau de résultats + graphique des performances. |
| **Vidéo démo** | Courte démonstration montrant le pipeline complet en action. | Lien vers la vidéo (YouTube ou fichier). |
| **Documentation** | Description technique, architecture, stack, limitations et suites possibles. | Ce dépôt + fichiers `docs/README.md` et schémas. |

---

## 🧩 Stack technique
| Domaine | Outil / Technologie | Justification |
|----------|--------------------|----------------|
| **Conteneurisation** | Docker | Standard de packaging, portable et simple à exécuter. |
| **Orchestration de tâches** | Apache Airflow | Orchestrateur open-source, très utilisé en data engineering. |
| **Monitoring** | Prometheus + Grafana | Duo open-source complet pour collecter et visualiser les métriques. |
| **Base de données** | SQLite / PostgreSQL | Facile à déployer localement et compatible avec Airflow. |
| **Déploiement** | Kubernetes (minikube / kind) | Standard de déploiement cloud-native, requis pour le livrable final. |

---

## 🧱 Plan d’architecture
Voici le schéma global du projet (format image) 👇  

📷 **Diagramme d’architecture (PNG)**  
<img width="3840" height="2175" alt="Untitled diagram _ Mermaid Chart-2025-10-06-153437" src="https://github.com/user-attachments/assets/710e42c1-193b-4975-8e6d-042b2cb66209" />


 Stack Technique – Projet 
Estimo
🎯 Objectif
Concevoir une infrastructure de données complète, containerisée et orchestrée, capable de :
collecter et agréger des données publiques immobilières (DVF, indicateurs communaux) ;


exposer un service d’estimation simple et transparent ;


surveiller et automatiser les traitements via des outils professionnels open-source.


Toute la stack repose sur des composants gratuits et open-source, déployables en local ou sur un cluster Kubernetes.

🧩 Vue d’ensemble
L’architecture Estimo s’appuie sur 6 briques principales :

Domaine
Technologie
Rôle clé
Frontend
Nginx
Sert la landing page statique du simulateur
Backend / API
FastAPI (Python)
Service REST qui calcule les estimations
Base de données
PostgreSQL
Stockage unique des données marché et utilisateurs
Orchestration / Automatisation
Apache Airflow
Planifie et exécute les traitements de données (ingestion DVF, agrégats, snapshots)
Monitoring / Observabilité
Prometheus + Grafana
Collecte et visualisation des métriques système et applicatives
Conteneurisation / Déploiement
Docker + Kubernetes (k3d)
Encapsulation, orchestration et scalabilité du projet
CI/CD & Outils de support
GitHub Actions + DBeaver (+ n8n optionnel)
Intégration continue, exploration BD, automatisations légères


🧠 
Justification détaillée des choix
1️⃣ Frontend – Nginx
Rôle : héberger une simple landing page statique contenant le formulaire d’estimation (HTML/CSS/JS).


Pourquoi ce choix ?


Léger, stable, et natif dans Docker.


Aucun framework JS nécessaire (Next/Vite non indispensables pour le MVP).


Requiert très peu de ressources.


Livrable attendu : démonstration visuelle du simulateur et connexion à l’API.



2️⃣ Backend – FastAPI (Python)
Rôle : cœur du projet. L’API reçoit les entrées utilisateur et calcule :


la valeur estimée du bien (median_price_m2 × surface) ;


la catégorie (Sous / Dans / Au-dessus du marché).


Pourquoi FastAPI ?


Performant et minimaliste, adapté aux APIs data-driven.


Auto-documentation Swagger → facilite la démo au jury.


Intégration native avec pandas, NumPy et scikit-learn (utile pour la phase ML).


Résultat attendu : un endpoint /estimate fonctionnel, mesurable en latence et exactitude.



3️⃣ Base de données – PostgreSQL
Rôle : stockage unique et central des trois univers de données :


DVF géolocalisée (transactions réelles nettoyées) ;


Indicateurs communaux (agrégats 2014–2024) ;


Entrées utilisateurs (estimations réalisées depuis le site).


Pourquoi Postgres ?


Gère les agrégats statistiques (percentiles, médianes) nécessaires à la table market_stats.


Solide, open-source, compatible SQL standard, et exploitable via DBeaver.


Peut héberger toutes les tables du star schema (dim/fact) dans un seul schéma logique.


Utilisation prévue :


Base “vérité marché” : market_stats, communes_market_yearly.


Base “utilisateurs” : estimation_input, fact_estimation.



4️⃣ Orchestration – Apache Airflow
Rôle : automatiser les tâches de préparation de données.


DAG #1 : ingestion et nettoyage du fichier DVF géolocalisé.


DAG #2 : calcul des statistiques marché (médianes/p25/p75 par zone).


DAG #3 : mise à jour des agrégats communaux.


Pourquoi Airflow ?


Mentionné explicitement dans la consigne (“Airflow DAG orchestration”).


Standard industriel open-source pour le scheduling et la traçabilité.


Interface claire pour le jury (exécution DAG visible en web UI).


Alternative complémentaire : n8n peut automatiser des notifications (alertes Slack, envoi email) mais ne remplace pas Airflow.



5️⃣ Monitoring – Prometheus + Grafana
Rôle : surveiller la santé de l’infrastructure et les KPIs métiers.


Prometheus collecte les métriques (API, Airflow, PostgreSQL).


Grafana les affiche dans deux dashboards :


Technique : CPU, mémoire, latence, erreurs 4xx/5xx, uptime.


Métier : nb d’estimations, répartition Sous/Dans/Au-dessus, volumes DVF traités.


Pourquoi ce duo ?

Exigence explicite du sujet (“Grafana monitoring dashboard”).

Standard open-source universel, facile à dockeriser et à configurer.

Livrable attendu : un dashboard Grafana provisionné accessible via le cluster.

6️⃣ Conteneurisation & Déploiement – Docker + Kubernetes (k3d/kind)
Rôle : uniformiser l’environnement de dev, puis démontrer le déploiement distribué.

Pourquoi Docker Compose ?
Simplicité pour le développement local et la démo initiale : une seule commande docker compose up.

Pourquoi Kubernetes (k3d ou kind) ?
Nécessité du livrable “Kubernetes deployment”.

Ces distributions locales sont gratuites et fonctionnent sur tout poste.
Elles permettent de montrer le kubectl get pods et l’Ingress fonctionnel (preuve d’orchestration).


Ingress : Traefik ou NGINX Ingress (un seul pour la démo).
Packaging : Helm pour déploiement modulaire (API, Airflow, Grafana).

Résultat attendu : cluster opérationnel et reproductible.



7️⃣ 
CI/CD – GitHub Actions
Rôle : automatiser la construction et la livraison des images Docker.


Pourquoi ce choix ?
Gratuit, directement intégré à GitHub.
Permet de valider le build, lancer les tests, et pousser les images dans un registre (GHCR ou Docker Hub).

Pipeline prévu :

Job 1 : lint + test API.

Job 2 : build/push des images.

Job 3 : (optionnel) déploiement automatique sur k3d.

8️⃣ Outils de support
DBeaver → client SQL pour explorer Postgres et valider les requêtes.
Raison : outil gratuit, multiplateforme, intuitif pour montrer les tables market_stats, fact_estimation pendant la soutenance.

n8n (optionnel) → automatisation visuelle (alertes DAG, notifications).
Raison : complément ergonomique à Airflow pour des automatisations “légères” (non data).

Make / scripts bash → pour lancer des benchmarks locaux.
wrk ou k6 → pour mesurer la latence API (preuve de performance).



🔐 Principes de sécurité et conformité
Aucune donnée personnelle conservée (adresses anonymisées → zone_key commune).

Accès à la base protégés par variables d’environnement / secrets Kubernetes.

Pas de services exposés en public hormis l’API via ingress.

Estimo – Simulateur de Valeur Immobilière

🎯 Vision
Estimo est une plateforme simple et accessible qui permet à n’importe quel utilisateur d’obtenir une estimation instantanée de la valeur de son bien immobilier sur le marché.
L’objectif est double :
Informer le grand public avec une estimation fiable et compréhensible.


Constituer une base de données riche pour affiner nos modèles de prédiction à partir de transactions réelles.



💡 Problématique
Aujourd’hui, beaucoup de propriétaires ou d’acheteurs ne savent pas si un prix de vente est au-dessus ou en dessous du marché réel.
Les simulateurs existants sont souvent :
opaques (peu d’explications sur le calcul),

limités (peu de critères pris en compte),
fermés (aucune ouverture des données).
Estimo veut rendre l’estimation immobilière transparente, éducative et évolutive.

🧩 Concept
Une landing page (page web simple et claire) permet de renseigner les caractéristiques d’un bien :
Localisation (adresse, code postal, commune)

Surface habitable
Nombre de pièces / chambres / salles de bain
Année de construction ou ancienneté
Type de logement (maison, appartement…)
Étiquette énergétique (DPE)
Autres atouts (balcon, parking, jardin…)

→ En un clic, le visiteur obtient :
une estimation du prix de marché (avec une fourchette),

un indice de positionnement :

 🔵 Sous le marché / 🟢 Dans le marché / 🔴 Au-dessus du marché,

une courte analyse expliquant les facteurs principaux (surface, zone, état, DPE…).

🧠 Valeur ajoutée
Pour l’utilisateur : vision claire, intuitive, et sans jargon.

Pour nous (techniquement) : les données collectées (anonymisées) alimentent une base d’apprentissage pour entraîner à terme un modèle de Machine Learning capable de prédire les prix de manière plus fine (type AVM – Automated Valuation Model).


📊 Sources de données
Nous nous appuierons sur des bases publiques fiables :
DVF / DVF+ : base nationale des transactions immobilières (prix, surfaces, localisation).


INSEE / BAN / DPE : informations géographiques, démographiques et énergétiques.


Ces données servent de référentiel de marché pour comparer les biens soumis par les utilisateurs.

🔐 Positionnement
Estimo n’est pas une agence ni un site d’annonces.
C’est un simulateur indépendant, fondé sur la donnée et la transparence.
Le but : démocratiser la data immobilière tout en préparant une infrastructure scalable (Docker + API + Data pipeline).

🚀 Étapes futures
Phase 1 – Landing page et API de simulation

 → capturer les entrées, retourner une estimation simple (basée sur statistiques locales).

Phase 2 – Base de données nationale + pipeline de nettoyage

 → construire les tables de référence du marché.

Phase 3 – Machine Learning

→ entraîner un modèle de prédiction (prix/m²) sur DVF + variables géographiques.

Phase 4 – Monitoring et dashboard

 → observer la qualité des estimations, performance et usage.






RGPD : données strictement agrégées, aucune PII.

