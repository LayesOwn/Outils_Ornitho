# ORNI-LAB — Programme de Formation

## Présentation générale

**ORNI-LAB** est un laboratoire pédagogique interactif pour l'écologie quantitative et la modélisation des populations d'oiseaux. Il regroupe **18 simulateurs** organisés en deux sections : Biostatistique et Dynamique des populations.

L'outil est conçu pour des étudiants de niveau **L3 à Master**, des enseignants souhaitant l'intégrer dans leurs cours, et des professionnels de terrain cherchant à explorer leurs données.

---

## Public visé

| Profil | Usage principal |
|--------|----------------|
| Étudiant L3/Master | Apprentissage des méthodes, TP, interprétation guidée |
| Enseignant | Démonstration en cours, création d'exercices, mode Enseignant |
| Professionnel terrain | Analyse de données CSV, PVA, scénarios de gestion |

---

## Deux modes d'utilisation

- **Mode Étudiant** : interface simplifiée, interprétations guidées, focus sur les résultats
- **Mode Enseignant** : formules LaTeX, notes pédagogiques détaillées, hypothèses et limites mathématiques de chaque modèle

---

## Cursus recommandé — 4 séances de 3 heures

### Séance 1 — Prise en main et biostatistiques de base
**Durée : 3h | Prérequis : aucun**

| Heure | Contenu |
|-------|---------|
| 0h00–0h30 | Installation, lancement, navigation dans l'interface |
| 0h30–1h00 | Analyse CSV — importer ses données, explorer, nettoyer |
| 1h00–1h45 | Statistiques descriptives — résumer une variable, histogramme |
| 1h45–2h30 | Corrélation et régression — relation entre deux variables |
| 2h30–3h00 | Export PDF/CSV — produire un résumé, discussion des résultats |

**Modules utilisés :** Analyse CSV, Statistiques descriptives, Corrélation & régression

---

### Séance 2 — Biostatistiques avancées
**Durée : 3h | Prérequis : Séance 1**

| Heure | Contenu |
|-------|---------|
| 0h00–0h45 | Tests statistiques — comparer deux groupes, t-test, ANOVA |
| 0h45–1h30 | GLM comptage — Poisson, binomial négatif pour abondances |
| 1h30–2h15 | Modèles mixtes — effets aléatoires, données groupées par site |
| 2h15–3h00 | Domaines vitaux (MCP/KDE) — analyser des données GPS |

**Modules utilisés :** Tests statistiques, GLM comptage, Modèle mixte, Domaine vital MCP, Domaine vital KDE

---

### Séance 3 — Dynamique des populations (fondamentaux)
**Durée : 3h | Prérequis : Séances 1 et 2**

| Heure | Contenu |
|-------|---------|
| 0h00–0h30 | Richesse & diversité — indices de Shannon, Simpson, courbes |
| 0h30–1h15 | Croissance exponentielle et logistique — r, K, N0 |
| 1h15–2h00 | Matrices de Leslie — projection structurée, lambda, élasticité |
| 2h00–3h00 | Capture-Marquage-Recapture — estimer une abondance cachée |

**Modules utilisés :** Richesse & diversité, Croissance, Matrices de Leslie, CMR

---

### Séance 4 — Dynamique des populations (avancé) et conservation
**Durée : 3h | Prérequis : Séances 1 à 3**

| Heure | Contenu |
|-------|---------|
| 0h00–0h30 | Modèles d'occupation — détectabilité imparfaite, ψ et p |
| 0h30–0h45 | Distance sampling — densité par transect |
| 0h45–1h15 | Lotka-Volterra — proie-prédateur, oscillations |
| 1h15–1h45 | Séries temporelles — tendances (Mann-Kendall) |
| 1h45–2h30 | PVA & conservation — risque de quasi-extinction stochastique |
| 2h30–3h00 | Scénarios de gestion — comparer des actions de conservation |

**Modules utilisés :** Occupation, Distance sampling, Lotka-Volterra, Séries temporelles, PVA, Scénarios de gestion

---

## Ressources disponibles

| Fichier | Description |
|---------|-------------|
| `01_GUIDE_INSTALLATION.md` | Installation pas-à-pas, lancement, interface |
| `03_PRESENTATION_DIAPORAMA.md` | Plan complet d'une présentation de 45 min |
| `fiches/FICHES_BIOSTATISTIQUE.md` | Fiches pédagogiques des 8 modules biostat |
| `fiches/FICHES_DYNAMIQUE.md` | Fiches pédagogiques des 10 modules dynamique |
| `TP/TP_SEANCE1.md` à `TP_SEANCE4.md` | Exercices guidés par séance |
| `../guide_scientifique.md` | Référence scientifique complète (variables, hypothèses) |

---

## Conseils pédagogiques généraux

1. **Demandez toujours aux étudiants de prédire** le résultat avant de bouger un curseur.
2. **Modifiez une variable à la fois** pour isoler son effet.
3. **Comparez toujours au moins deux scénarios** avant de conclure.
4. **Distinguez** : effet statistique ≠ effet biologique ≠ effet de gestion.
5. **Notez les hypothèses** non représentées dans le simulateur.
6. **Utilisez les exports CSV** pour faire recalculer un résultat en dehors d'ORNI-LAB.
