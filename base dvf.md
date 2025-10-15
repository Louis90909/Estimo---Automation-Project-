# Base DVF

[DVF par commune ](https://www.notion.so/DVF-par-commune-284a48aa950780a3b666ec18dd2a3d35?pvs=21)


## **Indicateurs immobiliers par commune et par année (2014–2024)**

**Fournisseur / Producteur :** *Boris Mericskay*

**Plateforme :** [data.gouv.fr – Indicateurs immobiliers par commune](https://www.data.gouv.fr/fr/datasets/indicateurs-immobiliers-par-commune-et-par-annee-prix-et-volumes-sur-la-periode-2014-2024/)

**Licence :** *Open Data Commons Open Database License (ODbL)*

**Dernière mise à jour :** *7 juillet 2025*

**Couverture temporelle :** *2014 → 2024*

**Grain d’analyse :** *Commune (code INSEE)* × *Année*

**Volume :** ~36 000 communes × 11 années

**Qualité :** Données dérivées et nettoyées du jeu **DVF géolocalisé** (transactions réelles)

---

### **📋 Description**

Ce jeu de données agrège, pour chaque **commune française** et pour chaque **année entre 2014 et 2024**, un ensemble d’indicateurs clés décrivant le marché immobilier résidentiel :

| **Variable** | **Description** |
| --- | --- |
| INSEE_COM | Code INSEE de la commune (clé de jointure) |
| annee | Année de référence |
| nb_mutations | Nombre total de ventes enregistrées |
| NbMaisons / NbApparts | Nombre de ventes de maisons / d’appartements |
| PropMaison / PropAppart | Proportion respective de maisons / appartements |
| PrixMoyen | Prix moyen des biens vendus (en €) |
| Prixm2Moyen | Prix moyen au m² (en €/m²) |
| SurfaceMoy | Surface moyenne des biens vendus (en m²) |

### **Méthodologie**

Les données sont issues d’un **traitement de la base DVF géolocalisée (DGFiP / Etalab)**.

L’auteur a appliqué une série de filtres garantissant la représentativité des ventes :

- Seules les **mutations “monoventes”** (une seule vente, sans lots multiples) sont conservées.
- **Plage de prix** : entre **15 000 € et 10 000 000 €**.
- **Surface** :
    - Appartements : entre **10 m² et 250 m²**
    - Maisons : entre **10 m² et 400 m²**
- **Prix au m²** : entre **330 € et 15 000 €/m²**.

👉 La méthodologie complète est publiée dans *Cybergeo* :

📖 https://journals.openedition.org/cybergeo/39583

---

### **🧠 Utilisation dans Estimo**

- Fournit une **vision consolidée par commune et par année** du marché résidentiel français.
- Sert de **référence de contrôle** pour nos agrégats calculés à partir du DVF brut.
- Permet un **fallback de prix** si un échantillon DVF local est trop faible ou absent :

```jsx
SELECT 
  i.id,
  c.Prixm2Moyen,
  (i.surface_habitable * c.Prixm2Moyen) AS estimated_price_baseline
FROM estimation_input i
JOIN communes_market_2024 c
  ON c.INSEE_COM = i.insee_commune;
```

- Utile pour **analyser les tendances temporelles** (hausse ou baisse par commune de 2014 à 2024).
- Possibilité d’intégrer ultérieurement un modèle temporel (prévision prix/commune).

---

### **🧩 Intégration dans le modèle de données**

- Stocké dans une table communes_market_yearly.
- **Clé primaire** : (insee_commune, annee)
- Jointure directe avec estimation_input.insee_commune.
- Exemple de structure :
