# Monitoring

## **Processus de Monitoring et Contrôle Qualité des Données**

### Objectif

Le monitoring du pipeline *Estimo* vise à garantir :

- La **traçabilité complète** des données depuis l’ingestion brute (DVF) jusqu’à leur exposition finale (*Grafana*, *API*, etc.)
- Le **contrôle qualité automatisé** des flux entrants et des transformations
- Le **suivi en temps réel** des exécutions, des erreurs et des performances via *Airflow*, *PostgreSQL* et *Grafana*

---

## Architecture de Monitoring

### Airflow — Orchestration et exécution des contrôles

Airflow orchestre toutes les étapes du pipeline :

- Ingestion (`ingest_dvf_full`)
- Transformation / Agrégation (`build_communes_market_2024`)
- Simulation utilisateur (`estimation_input_daily`)
- Vérifications de qualité et mise à jour Grafana (`run_quality_checks`, `mark_grafana_refresh`)

Chaque DAG est loggé dans Airflow, et ses métadonnées sont visibles via :

- **Airflow UI** → statut des tâches, historique des runs  
- **Tables de log PostgreSQL** → pour le suivi persistant côté base

---

### PostgreSQL — Stockage, contrôle et suivi

#### a) Table : `qa.check_results`

**Rôle :** journal central des contrôles qualité.  
Chaque exécution insère une ligne par test effectué.

| Champ | Description |
|-------|--------------|
| id | identifiant unique du contrôle |
| check_name | nom du test exécuté |
| status | PASS ou FAIL |
| observed | valeur observée |
| threshold | valeur seuil (si applicable) |
| details | informations complémentaires (JSON) |
| ts | horodatage d’exécution |

**Exemples de contrôles :**
- `dvf_full_raw_exists` → vérifie la présence des données brutes  
- `communes_market_2024_exists` → contrôle la table agrégée  
- `prix_m2_range` → détecte les valeurs aberrantes de prix au m²  

Ces contrôles permettent de **valider la qualité métier avant publication des données.**

---

#### b) Table : `grafana_refresh`

**Rôle :** assurer la synchronisation entre PostgreSQL et Grafana.  
Chaque mise à jour des données est marquée dans cette table.

| Champ | Description |
|-------|--------------|
| last_refreshed | date du dernier rafraîchissement |
| status | état de la synchronisation (*ok*, *error*) |

Cela permet d’automatiser le **rafraîchissement des dashboards Grafana** après chaque run réussi.

---

#### c) Table : `estimation_input`

**Rôle :** simulation utilisateur (données d’entrée pour test ou production).  
Elle permet de suivre :

- le **volume d’entrées traitées quotidiennement**
- la **distribution des caractéristiques** (surface, pièces, type de bien, etc.)
- la **cohérence avec les statistiques marché**

---

## Grafana — Visualisation et alertes

Grafana est connecté à la base PostgreSQL.  
Les dashboards affichent :

- L’état du pipeline (*succès/échec* des DAGs)
- Les derniers résultats de `qa.check_results`
- Le timestamp de `grafana_refresh`
- Les volumes de lignes traitées par table

Des **alertes automatiques** peuvent être déclenchées (*Slack*, *mail*) si un test **FAIL** est enregistré.
