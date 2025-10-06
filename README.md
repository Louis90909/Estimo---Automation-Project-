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
| **Automatisation complémentaire** | n8n (optionnel) | Automatiser des tâches simples sans code supplémentaire. |

---

## 🧱 Plan d’architecture
Voici le schéma global du projet (format image) 👇  

📷 **Diagramme d’architecture (PNG)**  
<img width="3840" height="2175" alt="Untitled diagram _ Mermaid Chart-2025-10-06-153437" src="https://github.com/user-attachments/assets/710e42c1-193b-4975-8e6d-042b2cb66209" />



```markdown
