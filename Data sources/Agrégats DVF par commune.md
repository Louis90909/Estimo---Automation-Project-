# **Agrégats DVF par commune –**

https://github.com/Louis90909/Estimo---Automation-Project-/blob/main/communesdvf2024.csv

# **année 2024**

**Fichier fourni :** communesdvf2024.csv

**Grain :** **commune (INSEE)** × **année 2024**

**Clé de jointure :** INSEE_COM (code commune INSEE)

### **Champs (observés dans le fichier)**

- INSEE_COM : code INSEE commune (**clé**)
- annee : 2024
- nb_mutations : nb total de ventes
- NbMaisons, NbApparts : nb de ventes maisons / appartements
- PropMaison, PropAppart : part (en %) des maisons / appartements
- PrixMoyen : prix moyen (EUR) par mutation
- Prixm2Moyen : **prix moyen au m²** (EUR/m²) sur la commune
- SurfaceMoy : surface moyenne des biens vendus (m²)

### **Pourquoi c’est utile (MVP)**

- **Baseline ultra-rapide** par commune : si on n’a pas encore calculé nos stats fines par *bucket* (surface/pièces), on peut estimer **Prix ≈ Prixm2Moyen × surface_habitable**.
- **Fallback** quand un bucket DVF est trop peu fourni (ex. n_samples faible).
- **Contrôle qualité** : comparer nos agrégats market_stats vs moyennes communales 2024.

### **Intégration dans notre schéma**

1. Créer une table de référence **commune 2024** :

```jsx
CREATE TABLE IF NOT EXISTS communes_market_2024 (
  insee_commune   TEXT PRIMARY KEY,
  nb_mutations    INTEGER,
  nb_maisons      INTEGER,
  nb_apparts      INTEGER,
  prop_maison     REAL,
  prop_appart     REAL,
  prix_moyen_eur  INTEGER,
  prix_m2_moyen   INTEGER,
  surface_moy_m2  INTEGER
);
```

1. Charger le CSV (outil au choix).
2. **Croisement simple** avec notre table d’insertion : on aligne zone_key sur le code INSEE (ou on garde insee_commune en plus) :

```jsx
-- Estimation baseline par commune (fallback)
SELECT 
  i.id,
  c.prix_m2_moyen,
  (i.surface_habitable * c.prix_m2_moyen) AS estimated_price_baseline
FROM estimation_input i
JOIN communes_market_2024 c
  ON c.insee_commune = i.insee_commune    -- ou i.zone_key si = INSEE
WHERE i.id = :estimation_id;
```

### **Bonnes pratiques / limites**

- **Année** : ce jeu est **2024** seulement → utile pour un instantané récent. Pour une vision multi-années, privilégier nos agrégats DVF (table market_stats).
- **Mélange types** : Prixm2Moyen mélange potentiellement maisons et appartements ; pour plus de précision, filtrer par type quand tu as market_stats.
- **Zones rurales** : si nb_mutations faible, considérer un **fallback départemental** ou Prixm2Moyen voisin.

