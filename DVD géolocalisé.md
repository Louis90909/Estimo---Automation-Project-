# DVD géolocalisé

##  Objectif

Afin d’assurer la fiabilité et la transparence de nos estimations, le projet **Estimo** s’appuie exclusivement sur des **bases de données publiques nationales**.

Ces sources constituent le socle de notre **référentiel marché**, et certaines alimenteront ultérieurement les modèles de Machine Learning destinés à la prédiction des prix immobiliers.

---

##  1. Demandes de Valeurs Foncières (DVF)

**Fournisseur :** Ministère de l’Économie, des Finances et de l’Industrie / DGFiP

**URL :** [data.gouv.fr - DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)

**Période :** 2019 – aujourd’hui (mis à jour semestriellement)

###  Description

La base DVF recense l’ensemble des **transactions immobilières notariales** réalisées en France métropolitaine et DOM-TOM (hors Alsace-Moselle).

Chaque enregistrement décrit une mutation (vente) avec :

- la **valeur foncière** (prix de vente réel),
- la **date de mutation**,
- la **nature du bien** (maison, appartement, dépendance),
- la **surface réelle bâtie**,
- le **nombre de pièces principales**,
- la **localisation administrative** (code postal, code commune, section cadastrale).

###  Utilisation dans Estimo

- Base principale pour construire les **statistiques de marché** (table market_stats).
- Calcul des indicateurs **prix/m² médian**, **p25/p75**, **nombre d’échantillons** par zone et type de bien.
- Alimentera à terme le modèle ML supervisé (régression de prix).

---

##  2. Demandes de Valeurs Foncières Géolocalisées (DVF+)

**Fournisseur :** Etalab / Cerema

**URL :** [data.gouv.fr - DVF géolocalisées](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees-dvf-geolocalisees/)

**Format :** GeoJSON / Parquet

###  Description

Version enrichie et géocodée du jeu DVF, chaque transaction est associée à :

- des **coordonnées géographiques précises** (latitude, longitude),
- un **identifiant de parcelle cadastrale**,
- des **données nettoyées et normalisées** par le Cerema.

###  Utilisation dans Estimo

- Permet d’affecter chaque vente à une **zone géographique homogène** (*commune*, *INSEE code* ou *geohash5*).
- Facilite les **jointures spatiales** avec d’autres référentiels (Cadastre, BDNB).
- Sert à dériver la clé zone_key utilisée dans nos tables.

---

##  3. Base Adresse Nationale (BAN)

**Fournisseur :** IGN, La Poste, Etalab

**URL :** https://adresse.data.gouv.fr/

###  Description

La BAN référence toutes les **adresses normalisées de France** avec :

- numéro, voie, code postal, commune,
- identifiant unique,
- coordonnées géographiques (lat/lon).

###  Utilisation dans Estimo

- **Géocodage direct** des adresses saisies sur la landing page utilisateur.
- Conversion des adresses → coordonnées → zone_key (code INSEE ou geohash5).
- Assure la cohérence entre les données saisies et les données de référence (DVF+).

---

##  4. Base de Données Nationale des Bâtiments (BDNB)

**Fournisseur :** CSTB (Centre Scientifique et Technique du Bâtiment)

**URL :** [data.gouv.fr - BDNB](https://www.data.gouv.fr/fr/datasets/base-de-donnees-nationale-des-batiments-bdnb/)

###  Description

Regroupe des informations détaillées sur plus de **20 millions de bâtiments** :

- année de construction,
- nombre d’étages, surface au sol,
- performance énergétique estimée,
- typologie et usage du bâtiment.

###  Utilisation dans Estimo

- Enrichissement optionnel des données DVF pour la **phase de modélisation avancée (ML)**.
- Ajout de variables explicatives : *ancienneté, hauteur, DPE estimé*, etc.
- Permet d’affiner les estimations selon les caractéristiques structurelles des biens.

---

##  5. Cadastre

**Fournisseur :** DGFiP via data.gouv.fr

**URL :** [data.gouv.fr - Cadastre](https://www.data.gouv.fr/fr/datasets/cadastre/)

###  Description

Le cadastre fournit la **géométrie des parcelles cadastrales** et leur surface.

Il permet d’étudier la forme, la taille et la densité des parcelles associées à chaque bien immobilier.

###  Utilisation dans Estimo

- Jointure spatiale (par identifiant de parcelle) pour connaître la **surface totale du terrain**.
- Utile pour estimer le **ratio terrain/bâti**, indicateur fort de la valeur d’un bien en zone périurbaine.
- Non essentiel au MVP, mais exploitable à moyen terme.

---

##  6. Registre National d’Immatriculation des Copropriétés (RNIC)

**Fournisseur :** Agence Nationale de l’Habitat (ANAH)

**URL :** [data.gouv.fr - RNIC](https://www.data.gouv.fr/fr/datasets/registre-national-dimmatriculation-des-coproprietes-rnic/)

###  Description

Répertoire officiel des copropriétés en France :

- identifiant du syndicat de copropriété,
- année de construction, nombre de lots, adresse, surface du bâti, etc.

###  Utilisation dans Estimo

- Donne un contexte pour les **appartements** (taille de l’immeuble, ancienneté, nb de lots).
- Permet d’affiner les estimations sur le segment collectif (différencier un petit immeuble d’un grand ensemble).
- Intégré à une phase ultérieure du projet (apprentissage et enrichissement).

---

##  Synthèse d’utilisation

| **Source** | **Rôle dans Estimo** | **Stade d’intégration** | **Données extraites principales** |
| --- | --- | --- | --- |
| **DVF+** | Référence des transactions | ✅ Phase 1 (MVP) | Prix, surface, type, date, commune |
| **BAN** | Géocodage adresses utilisateurs | ✅ Phase 1 (API) | Adresse → coord. GPS / INSEE |
| **BDNB** | Caractéristiques bâtiment | 🕒 Phase 2 (ML) | Année, étage, DPE, surface |
| **Cadastre** | Ratio terrain/bâti | 🕒 Phase 2 | Surface terrain |
| **RNIC** | Détails copropriété | 🕒 Phase 3 | Nb lots, âge immeuble |

| **Base** | **Usage** | **Priorité** | **Intégration** |
| --- | --- | --- | --- |
| **DVF / DVF+** | Référentiel de prix / transactions réelles | 🟢 **Essentielle** | Peupler market_stats |
| **BAN** | Géocodage adresse utilisateur → zone | 🟢 **Essentielle** | API /estimate |
| **Cadastre** | Parcelles / surfaces terrain | 🟠 Optionnel | Croisement spatial |
| **BDNB** | Caractéristiques bâtiments | 🟠 Optionnel | Enrichir modèle ML |
| **RNIC** | Infos copropriétés | 🟡 Secondaire | Spécifique appartements |
