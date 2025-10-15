# 1. ingest_dvf_full.py

### **But : ingestion brute du fichier full.csv.gz dans PostgreSQL**

Ce DAG charge **toutes les données DVF 2024** dans la table dvf_full_raw.

###  Étapes principales :

1. **Vérifie que le fichier** /opt/airflow/data/full.csv.gz est présent.
2. **Décompresse** le CSV.
3. **Lit et insère** les lignes dans Postgres (estimo-db) via COPY ou psycopg2.

###  Objectif :

Avoir la table brute dvf_full_raw propre, unique et exploitable pour les traitements en aval.

###  En résumé :

> “C’est le point d’entrée du pipeline DVF — il ingère la donnée brute dans le cluster.”
>
>


# **2. load_communes_2024.py**

### **But : contrôle ou chargement d’un CSV pré-agrégé communal**

Ce DAG servait de test initial : il prenait un fichier déjà agrégé (communesdvf2024.csv) et le chargeait dans la base sous une table type ref.communes_market_yearly.

###  Étapes :

- Vérif du CSV local (communesdvf2024.csv)
- Copie dans /opt/airflow/data/
- Chargement dans une table Postgres

###  Objectif :

Simuler un import “manuel” de référence avant de produire l’agrégat automatiquement.

###  En résumé :

> “DAG de test pour valider la chaîne Airflow → Postgres avec un petit fichier.”



# **3. check_quality.py**

### But : vérifications qualité sur les données DVF

Ce DAG vérifie qu’on a bien chargé les données DVF (par ex. COUNT(*) > 0).

###  Étapes typiques :

- Connexion Postgres (estimo_postgres)
- Vérifie que la table dvf_full_raw existe
- Vérifie que le nombre de lignes > seuil (sanity check)

###  Objectif :

Détecter tout problème d’ingestion ou de vide avant d’exécuter les traitements en aval.

###  En résumé :

> “Garde-fou automatique avant les agrégations ou modèles.”


# **4 build_communes_market_2024**

### 

### **Objectif**

Ce DAG automatise la **construction des indicateurs immobiliers par commune** pour l’année 2024, à partir du jeu brut **DVF (Demande de Valeurs Foncières)** précédemment importé dans la base.

C’est un **pipeline d’agrégation** qui transforme les transactions unitaires (chaque vente immobilière) en **statistiques agrégées** par commune.

---

### 

### **Fonctionnement**

1. **Synchronisation avec le DAG ingest_dvf_full**
    
    Il attend que le DAG d’ingestion des données DVF soit **terminé avec succès** (grâce à l’ExternalTaskSensor).
    
    → Cela garantit que les données sont bien chargées avant de commencer les calculs.
    
2. **Création de la table communes_market_2024**
    
    Si elle n’existe pas, elle est créée automatiquement dans PostgreSQL avec la structure prévue (une ligne par commune).
    
3. **Agrégation des ventes 2024**
    
    Le DAG calcule, pour chaque **code INSEE de commune** :
    
    - nb_mutations → nombre total de ventes
    - nb_maisons, nb_apparts → volumes par type
    - prop_maison, prop_appart → proportions
    - prix_moyen_eur, prix_m2_moyen, surface_moy_m2 → indicateurs de prix et de surface moyens
    
    Les résultats sont insérés ou mis à jour dans la table communes_market_2024.
    

---

### 

### **Rôle dans le pipeline global**

- Il transforme la donnée **transactionnelle brute** (chaque mutation DVF) en **vision agrégée du marché**.
- Sert ensuite de **base de référence** pour :
    - l’analyse exploratoire (prix moyen par commune)
    - la création de **dashboards** (Grafana)
    - les modèles de prédiction (fallback “prix au m² communal”)
- Il constitue donc une **couche analytique intermédiaire** dans le pipeline Estimo.

# **5. DAG – estimo_master**

### **Objectif**

Ce DAG est le **chef d’orchestre du pipeline Estimo**.

Il automatise toute la chaîne de traitement des données DVF (Demande de Valeurs Foncières) — depuis l’ingestion brute jusqu’à la création des indicateurs agrégés par commune.

En d’autres termes : il **enchaîne automatiquement plusieurs DAGs** pour exécuter le flux complet de bout en bout, sans intervention manuelle.

---

### **Fonctionnement**

Le DAG suit **4 étapes principales** :

1. **Déclenchement du DAG d’ingestion (ingest_dvf_full)**
    
    → Télécharge et charge dans PostgreSQL le fichier brut full.csv contenant toutes les transactions DVF 2024.
    
2. **Attente de la fin du DAG d’ingestion**
    
    → Le DAG reste en pause jusqu’à ce que ingest_dvf_full soit terminé avec succès (grâce à un ExternalTaskSensor).
    
3. **Déclenchement du DAG d’agrégation (build_communes_market_2024)**
    
    → Une fois la donnée brute disponible, il construit automatiquement les statistiques par commune (prix moyen, nb de ventes, etc.).
    
4. **Vérification de la fin de l’agrégat**
    
    → Le DAG s’assure que build_communes_market_2024 s’est bien exécuté avant de conclure le run global.
    

---

### **Planification**

- Par défaut, il est configuré pour une exécution **quotidienne (@daily)**.
- Tu peux ajuster le schedule pour un autre rythme (ex. @weekly ou @hourly) selon ton besoin.

| **Étape** | **DAG associé** | **Rôle** |
| --- | --- | --- |
| 1️⃣ | ingest_dvf_full | Charger les données DVF brutes dans la base PostgreSQL |
| 2️⃣ | build_communes_market_2024 | Agréger et calculer les indicateurs par commune |
| 3️⃣ | estimo_master | Orchestrer l’ensemble et automatiser le flux complet |

Grâce à ce DAG :

- L’ingestion et les agrégations s’enchaînent automatiquement.
- Le pipeline devient **entièrement autonome** et reproductible.
- Il garantit la **fraîcheur quotidienne** des données agrégées.

### **Bénéfices**

- Plus besoin de déclencher manuellement chaque étape.
- Facile à superviser depuis l’interface Airflow (une seule exécution déclenche toute la chaîne).
- Simplifie les **déploiements et la maintenance**.
- Sert de **base pour ajouter d’autres étapes** (ex. qualité, export, reporting, ML).

---

# **6. quality_checks_2024**

### **Objectif**

Assurer le **contrôle qualité automatique** des données DVF et des agrégats 2024 afin de garantir fiabilité, cohérence et plages de valeurs réalistes.

### **Ce que le DAG vérifie**

- Présence de la table brute dvf_full_raw.
- Présence de l’agrégat communes_market_2024.
- Absence de NULL sur la clé insee_commune.
- Plages réalistes :
    - prix_m2_moyen ∈ [330 ; 20 000]
    - surface_moy_m2 ∈ [10 ; 500]
    - prop_maison, prop_appart ∈ [0 ; 100]
- Chaque test écrit un résultat PASS/FAIL dans qa.check_results.

### **Orchestration**

- Attend la fin de ingest_dvf_full puis de build_communes_market_2024.
- Exécute les checks.
- Échoue le run si un check est en échec.

### **Sorties**

- Table qa.check_results pour l’historique des contrôles.
- Logs Airflow pour diagnostic rapide.
- Intégrable dans Grafana/Tableau pour monitoring.

### **Bénéfices**

- Pipeline **observé** et **fiable**.
- KOs détectés tôt, avec trace en base.
- Preuve de conformité et de monitoring pour les livrables.

# **7. estimation_input_daily**

## **Objectif**

Automatiser, chaque jour, l’alimentation contrôlée du dataset **estimation_input** à partir d’échantillons synthétiques cohérents avec le marché, lancer les **contrôles qualité**, puis signaler à Grafana qu’un **rafraîchissement** est disponible.

## **Périmètre**

- **Dataset cible** : estimation_input
- **Sources** : communes_market_2024 (pour choisir des communes plausibles)
- **Contrôles** : DAG quality_checks_2024
- **Signalisation monitoring** : table grafana_refresh

## **Planification**

- **Cron** : 30 3 * * * (tous les jours à 03:30 UTC)
- **Catchup** : désactivé (exécution “jour courant” uniquement)

## **Chaîne de tâches**

1. **seed_estimation_input**
    - Insère ~200 lignes synthétiques/jour.
    - Valeurs générées avec distributions simples (type de bien, surface, pièces, DPE…).
    - Calcule les “buckets” (surface_bucket, rooms_bucket, built_period, energy_bucket).
    - Renseigne zone_key à partir d’une commune tirée aléatoirement dans communes_market_2024.
2. **run_quality_checks**
    - Déclenche le DAG **quality_checks_2024** et attend la fin.
    - Les résultats s’écrivent dans **qa.check_results** (statut PASS/FAIL + métriques).
3. **mark_grafana_refresh**
    - Upsert dans **grafana_refresh** (last_refreshed = now(), status='ok').
    - Sert de **marqueur** pour forcer/indiquer un refresh des dashboards.

## **Entrées / Sorties**

- **Entrées** : communes_market_2024 (existante et peuplée)
- **Sorties** :
    - estimation_input (lignes ajoutées quotidiennement)
    - qa.check_results (résultats QA)
    - grafana_refresh (timestamp de rafraîchissement)

## **Prérequis**

- Connexion Airflow **estimo_postgres** valide.
- Tables existantes :
    - communes_market_2024 (remplie)
    - estimation_input (schéma MVP)
    - qa.check_results (créée par la mise en place QA)
    - grafana_refresh (créée au premier run)

## **Supervision & validation rapide**

- **Airflow UI** → DAG **estimation_input_daily** : état des tâches et logs.
- **Comptages** :
    - SELECT COUNT(*) FROM estimation_input;
    - SELECT * FROM qa.check_results ORDER BY id DESC LIMIT 10;
    - SELECT * FROM grafana_refresh;

## **Scénarios d’échec courants & résolutions**

- **seed_estimation_input échoue** :
    - Vérifier l’existence et le volume de communes_market_2024.
    - Vérifier les droits d’écriture sur estimation_input.
- **run_quality_checks en échec** :
    - Ouvrir les logs du DAG quality_checks_2024.
    - Inspecter qa.check_results pour identifier le check en FAIL.
- **mark_grafana_refresh échoue** :
    - Vérifier que le schéma par défaut permet l’upsert.
    - Créer manuellement la table si besoin.

## **Bonnes pratiques**

- Garder le **volume journalier** modéré (200–1000 lignes) pour éviter de gonfler la table en dev.
- Purge possible (dev) : supprimer les lignes plus anciennes que X jours.
- Connecter Grafana à grafana_refresh pour afficher la **dernière exécution**.

## **Pourquoi ce DAG est utile**

- Il **simule un flux réel** d’entrées utilisateurs en l’absence de front.
- Il **garantit** qu’à chaque run, la donnée est **contrôlée** avant d’être consommée.
- Il **aligne** la stack Data → QA → Monitoring, livrable clé du projet.
