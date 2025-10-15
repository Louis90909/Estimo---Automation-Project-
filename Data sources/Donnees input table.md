# DONNEE INPUT TABLE

# **1) Principe**

- **Table A — estimation_input** : tout ce que l’utilisateur saisit (et quelques dérivés utiles).
- **Table B — market_stats** : nos références “marché” agrégées depuis la base nationale (par zone + type + tranches).
- **Croisement** : JOIN sur (zone_key, property_type_code, surface_bucket, rooms_bucket) pour calculer prix estimé & catégorie (Sous/Dans/Au-dessus).

---

# **2) Schéma minimal (SQL — compatible SQLite/Postgres)**

## **A) Données saisies —**

## **estimation_input**

```jsx
CREATE TABLE estimation_input (
  id                INTEGER PRIMARY KEY,             -- SERIAL en Postgres
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  -- Localisation (pas de PII stockée : adresse non conservée)
  postal_code       TEXT,                            -- ex: '75011'
  insee_commune     TEXT,                            -- ex: '75111'
  lat               REAL,                            -- optionnel
  lon               REAL,                            -- optionnel
  zone_key          TEXT NOT NULL,                   -- ex: geohash5 ou insee_commune

  -- Caractéristiques
  property_type_code TEXT NOT NULL,                  -- cf. KV ci-dessous
  surface_habitable  REAL NOT NULL,                  -- en m²
  rooms              INTEGER,                        -- pièces principales
  bedrooms           INTEGER,
  bathrooms          INTEGER,
  toilets            INTEGER,
  floor_level        INTEGER,                        -- étage (appart)
  has_elevator       BOOLEAN,
  parking_spaces     INTEGER,
  balcony_area       REAL,                           -- m² (balcon/terrasse)
  terrace_area       REAL,
  garden_area        REAL,
  year_built         INTEGER,
  energy_label_code  TEXT,                           -- DPE (A..G)
  ges_label_code     TEXT,                           -- GES (A..G)
  condition_score    INTEGER,                        -- 1..5

  -- Prix déclaré (optionnel) pour la catégorisation "au-dessus/sous le marché"
  listing_price_eur  REAL,

  -- Dérivés utiles (remplis côté API avant insert)
  surface_bucket     TEXT NOT NULL,                  -- ex: '30-50', '50-70'
  rooms_bucket       TEXT NOT NULL,                  -- ex: '1', '2', '3', '4', '5+'
  built_period       TEXT,                           -- ex: '<1948', '1949-1974', '1975-2000', '2001+'
  energy_bucket      TEXT,                           -- ex: 'A-B', 'C-D', 'E-G'

  -- Pour extensions légères sans casser le schéma
  extras_json        TEXT                            -- JSON (clé-valeur libre)
);

-- Index utiles
CREATE INDEX idx_input_zone ON estimation_input(zone_key);
CREATE INDEX idx_input_join ON estimation_input(zone_key, property_type_code, surface_bucket, rooms_bucket);
```

**B) Statistiques marché — market_stats**

### **Schéma**

Pour la description étendue de la signification des champs, nous vous recommandons de consulter la [notice officielle](https://www.data.gouv.fr/fr/datasets/r/d573456c-76eb-4276-b91c-e6b9c89d6656).

- **`id_mutation`** : Identifiant de mutation (non stable, sert à grouper les lignes)
- **`date_mutation`** : Date de la mutation au format ISO-8601 (YYYY-MM-DD)
- **`numero_disposition`** : Numéro de disposition
- **`nature_mutation`** : Nature de la mutation
- **`valeur_fonciere`** : Valeur foncière (séparateur décimal = point)
- **`adresse_numero`** : Numéro de l'adresse
- **`adresse_suffixe`** : Suffixe du numéro de l'adresse (B, T, Q)
- **`adresse_code_voie`** : Code FANTOIR de la voie (4 caractères)
- **`adresse_nom_voie`** : Nom de la voie de l'adresse
- **`code_postal`** : Code postal (5 caractères)
- **`code_commune`** : Code commune INSEE (5 caractères)
- **`nom_commune`** : Nom de la commune (accentué)
- **`ancien_code_commune`** : Ancien code commune INSEE (si différent lors de la mutation)
- **`ancien_nom_commune`** : Ancien nom de la commune (si différent lors de la mutation)
- **`code_departement`** : Code département INSEE (2 ou 3 caractères)
- **`id_parcelle`** : Identifiant de parcelle (14 caractères)
- **`ancien_id_parcelle`** : Ancien identifiant de parcelle (si différent lors de la mutation)
- **`numero_volume`** : Numéro de volume
- **`lot_1_numero`** : Numéro du lot 1
- **`lot_1_surface_carrez`** : Surface Carrez du lot 1
- **`lot_2_numero`** : Numéro du lot 2
- **`lot_2_surface_carrez`** : Surface Carrez du lot 2
- **`lot_3_numero`** : Numéro du lot 3
- **`lot_3_surface_carrez`** : Surface Carrez du lot 3
- **`lot_4_numero`** : Numéro du lot 4
- **`lot_4_surface_carrez`** : Surface Carrez du lot 4
- **`lot_5_numero`** : Numéro du lot 5
- **`lot_5_surface_carrez`** : Surface Carrez du lot 5
- **`nombre_lots`** : Nombre de lots
- **`code_type_local`** : Code de type de local
- **`type_local`** : Libellé du type de local
- **`surface_reelle_bati`** : Surface réelle du bâti
- **`nombre_pieces_principales`** : Nombre de pièces principales
- **`code_nature_culture`** : Code de nature de culture
- **`nature_culture`** : Libellé de nature de culture
- **`code_nature_culture_speciale`** : Code de nature de culture spéciale
- **`nature_culture_speciale`** : Libellé de nature de culture spéciale
- **`surface_terrain`** : Surface du terrain
- **`longitude`** : Longitude du centre de la parcelle concernée (WGS-84)
- **`latitude`** : Latitude du centre de la parcelle concernée (WGS-84)

### 

---

# **3) Listes**

# **clé-valeur**

# **(codes) à utiliser côté UI/API**

*(Pas besoin de tables séparées pour le MVP — on standardise les valeurs.)*

### **property_type_code**

| **code** | **label** |
| --- | --- |
| APT | Appartement |
| HSE | Maison |
| STD | Studio/T1 |
| OTH | Autre |

### **energy_label_code**

### **(DPE)**

A, B, C, D, E, F, G  *(si inconnu → NULL)*

### **ges_label_code**

A, B, C, D, E, F, G  *(optionnel)*

### **surface_bucket**

'0-30', '30-50', '50-70', '70-100', '100-150', '150+'

### **rooms_bucket**

'1', '2', '3', '4', '5+'

### **built_period**

'<1948', '1949-1974', '1975-2000', '2001+' *(si non renseigné → NULL)*

### **energy_bucket**

'A-B', 'C-D', 'E-G' *(dérivé de energy_label_code)*

> Ces
> 
> 
> **KV**
> 

---

# **4) Règles de dérivation (bucketisation côté API)**

- surface_bucket:
    - 0–30, 30–50, 50–70, 70–100, 100–150, 150+
- rooms_bucket:
    - <=1 → '1', 2, 3, 4, >=5 → '5+'
- built_period:
    - year_built: <1948, 1949–1974, 1975–2000, >=2001
- energy_bucket:
    - A,B → 'A-B'; C,D → 'C-D'; E,F,G → 'E-G'

---

# **5) Exemple d’insertion (utilisateur → estimation_input)**

```jsx
INSERT INTO estimation_input(
  zone_key, property_type_code, surface_habitable, rooms, bedrooms,
  bathrooms, floor_level, has_elevator, parking_spaces,
  balcony_area, terrace_area, garden_area, year_built,
  energy_label_code, condition_score, listing_price_eur,
  postal_code, insee_commune, lat, lon,
  surface_bucket, rooms_bucket, built_period, energy_bucket, extras_json
) VALUES (
  'u09tv', 'APT', 52.0, 2, 1,
  1, 3, 1, 0,
  4.5, 0, 0, 1998,
  'C', 3, 315000.0,
  '75011', '75111', NULL, NULL,
  '50-70', '2', '1975-2000', 'C-D', '{"renov":"partielle"}'
);
```

# **6) Ce qu’on a “by design”**

- **Simplicité** : 2 tables, une clé de jointure claire.
- **Évolutivité** : on pourra raffiner market_stats (ajouter d’autres dimensions) sans toucher estimation_input.
- **Flexibilité** : extras_json pour capturer des champs rares sans migration SQL.
- **Portage** : SQLite → Postgres sans changement conceptuel.

Si tu veux, je te prépare ensuite :

- un **diagramme** (mermaid) des deux tables et de la jointure,
- un **script de bucketisation** (Python) pour garantir les valeurs KV,
- et 2–3 **requêtes SQL** prêtes à l’emploi (estimation & catégorisation).
