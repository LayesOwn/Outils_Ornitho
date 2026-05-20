# TP Séance 1 — Prise en main et biostatistiques de base

**Durée :** 3 heures | **Public :** L3/Master | **Prérequis :** aucun

**Objectifs :**
- Installer et lancer ORNI-LAB
- Importer et explorer un fichier CSV de terrain
- Calculer des statistiques descriptives
- Interpréter une régression linéaire simple

---

## Partie 0 — Installation (30 min)

### 0.1 Lancer l'application

1. Double-cliquer sur `ORNI-LAB.bat`
   - Si l'application ne se lance pas, ouvrir PowerShell et lancer `python -m streamlit run app.py`
2. L'application s'ouvre dans le navigateur sur `http://localhost:8501`
3. Observer l'interface : barre latérale (gauche) et zone principale (droite)

### 0.2 Explorer les modes

1. Dans la barre latérale, cliquer sur **Mode Étudiant**
2. Observer l'interface du module "Statistiques descriptives"
3. Basculer sur **Mode Enseignant**
4. Identifier les éléments supplémentaires (formules, notes pédagogiques)

**Question 0.1 :** Citer deux informations supplémentaires visibles en Mode Enseignant par rapport au Mode Étudiant.

---

## Partie 1 — Analyse CSV (45 min)

### Contexte
Vous disposez d'un jeu de données de comptages d'oiseaux nicheurs sur 80 points d'écoute répartis dans trois habitats (forêt, prairie, bocage). Le fichier contient les colonnes : `site`, `habitat`, `espece`, `comptage`, `annee`, `longitude`, `latitude`.

### 1.1 Créer un fichier CSV d'exemple

Créer un fichier `points_ecoute.csv` avec le contenu suivant (ou utiliser le fichier fourni par l'enseignant) :

```csv
site,habitat,espece,comptage,annee
A1,foret,Fauvette des jardins,4,2023
A2,foret,Merle noir,7,2023
A3,foret,Mésange bleue,12,2023
B1,prairie,Alouette des champs,9,2023
B2,prairie,Bruant proyer,3,2023
B3,prairie,Tarier pâtre,5,2023
C1,bocage,Pie-grièche écorcheur,2,2023
C2,bocage,Linotte mélodieuse,8,2023
C3,bocage,Tourterelle des bois,1,2023
```

### 1.2 Importer et explorer

1. Dans la barre latérale, sélectionner **Section Biostatistique > Analyse CSV**
2. Importer le fichier CSV
3. Observer le résumé automatique : nombre de lignes, colonnes, valeurs manquantes, types de colonnes

**Question 1.1 :** Combien de colonnes numériques et catégoriques sont détectées automatiquement ?

4. Sélectionner la colonne `comptage` pour l'analyse de distribution
5. Observer l'histogramme et la boîte à moustaches

**Question 1.2 :** La distribution du comptage est-elle symétrique ? Comment le sait-on ?

### 1.3 Explorer une relation

1. Choisir `comptage` comme variable Y
2. (Si disponible) Explorer la relation entre deux variables numériques
3. Observer le R² et la p-value de la régression

### 1.4 Comparer deux habitats

1. Choisir `comptage` comme variable numérique
2. Choisir `habitat` comme variable catégorielle
3. Sélectionner deux habitats à comparer (ex. : forêt vs prairie)
4. Observer la p-value du test de Welch et les intervalles de confiance

**Question 1.3 :** La différence entre la forêt et la prairie est-elle statistiquement significative ? Est-elle biologiquement importante ?

### 1.5 Exporter

1. Télécharger le résumé en PDF
2. Télécharger les données nettoyées en CSV

---

## Partie 2 — Statistiques descriptives (45 min)

### 2.1 Simuler et explorer

1. Aller dans **Statistiques descriptives**
2. Régler : Nombre de sites = 60, Abondance moyenne = 10, Agrégation = faible
3. Lire les indicateurs : moyenne, médiane, écart-type, min, max
4. Observer l'histogramme

**Question 2.1 :** Avec une faible agrégation, la distribution est-elle proche d'une loi normale ? Quelle est la valeur de la médiane par rapport à la moyenne ?

### 2.2 Augmenter l'agrégation

5. Augmenter l'agrégation spatiale (curseur vers le maximum)
6. Observer les changements sur la distribution et les indicateurs

**Question 2.2 :** Comment la différence moyenne - médiane évolue-t-elle avec l'agrégation ? Pourquoi les ornithologues s'attendent-ils à des distributions agrégées ?

### 2.3 Stabilité des indicateurs

7. Réduire le nombre de sites à 10
8. Observer la variabilité des indicateurs
9. Remonter à 200 sites

**Question 2.3 :** Quel est l'effet de l'augmentation du nombre de sites sur la précision des indicateurs (médiane, écart-type) ?

### 2.4 Comparer deux habitats (si disponible dans le module)

10. Simuler deux groupes (forêt vs prairie) avec des abondances différentes
11. Comparer visuellement les boîtes à moustaches

---

## Partie 3 — Corrélation et régression (45 min)

### Contexte
On cherche à explorer la relation entre la **longueur de l'aile** (mm) et la **masse corporelle** (g) chez la Fauvette des jardins (*Sylvia borin*).

### 3.1 Petite taille d'échantillon

1. Aller dans **Corrélation & régression**
2. Régler : n = 15, pente = 3.5 g/mm, variabilité individuelle = faible
3. Observer r de Pearson, R², et p-value
4. Tracer le nuage de points avec la droite de régression

**Question 3.1 :** Avec n = 15 et une relation modérée (r ≈ 0.55), la p-value est-elle significative (< 0.05) ? Que conclut-on ?

### 3.2 Augmenter la taille d'échantillon

5. Conserver la même pente et la même variabilité
6. Passer de n = 15 à n = 150
7. Observer l'évolution de la p-value

**Question 3.2 :** La relation entre l'aile et la masse est-elle plus "forte" avec n = 150 qu'avec n = 15 ? Pourquoi la p-value change-t-elle ?

### 3.3 Relation nulle

8. Régler la pente à 0 (aucune relation)
9. Observer ce qui se passe pour différentes valeurs de n

**Question 3.3 :** Avec n = 200 et une pente nulle, la p-value est parfois < 0.05 par hasard. Que cela illustre-t-il sur le risque d'erreur de type I ?

### 3.4 Interprétation biologique

10. Pente = 2.8 g/mm, intercept = 5.2
11. Un individu a une longueur d'aile de 70 mm. Quelle masse prédit la régression ?
12. Un individu mesure 55 mm. La prédiction a-t-elle un sens biologique ? (Vérifier que 55 mm est dans la plage des données)

**Question 3.4 :** L'intercept = 5.2 g signifie "une fauvette avec une aile de 0 mm pèse 5.2 g". Pourquoi cette interprétation est-elle absurde ? Que signifie réellement l'intercept ?

---

## Partie 4 — Export et synthèse (15 min)

### 4.1 Produire un résumé PDF

1. Dans n'importe quel module actif, cliquer sur "Exporter PDF"
2. Ouvrir le PDF et identifier : les paramètres utilisés, les résultats clés, l'interprétation

### 4.2 Questions de synthèse

**Question 4.1 :** Dans la séance d'aujourd'hui, quelle méthode s'adapte le mieux à l'analyse de vos données de terrain ? Justifier.

**Question 4.2 :** Citer une situation où la moyenne est un mauvais résumé d'une distribution ornithologique.

**Question 4.3 :** Un collègue annonce "j'ai trouvé une corrélation significative (p = 0.01) entre la richesse spécifique et la surface du site." Quelles questions lui posez-vous avant d'accepter ce résultat ?

---

## Récapitulatif des formules à retenir

| Indicateur | Formule ou définition |
|------------|----------------------|
| Médiane | Valeur centrale de la distribution ordonnée |
| Écart-type | √(Σ(xᵢ - x̄)² / (n-1)) |
| r de Pearson | Cov(X,Y) / (σ_X × σ_Y), ∈ [-1, 1] |
| R² | r², proportion de variance expliquée |
| p-value | P(résultat aussi extrême | H₀ vraie) |

---

## Pour aller plus loin

- Lire la fiche scientifique : `docs/guide_scientifique.md` (sections Statistiques descriptives, Corrélation)
- Explorer le module **Tests statistiques** (Séance 2) pour comparer formellement plusieurs groupes
- Essayer d'importer un vrai fichier de terrain (données de baguage, atlas, LPO, STOC)
