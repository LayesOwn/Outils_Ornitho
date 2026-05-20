# TP Séance 4 — Dynamique avancée et conservation

**Durée :** 3 heures | **Public :** L3/Master | **Prérequis :** Séances 1 à 3

**Objectifs :**
- Estimer l'occupation et la détectabilité (modèles d'occupation)
- Estimer une densité par distance sampling
- Analyser une tendance temporelle (Mann-Kendall)
- Réaliser une PVA et comparer des scénarios de conservation

---

## Partie 1 — Modèles d'occupation (30 min)

### Contexte
On cherche à estimer la probabilité d'occupation du Pic noir (*Dryocopus martius*) dans 50 placettes forestières. Chaque placette est visitée 4 fois. La détectabilité du Pic noir varie avec la saison.

### 1.1 Sans correction de détectabilité

1. Aller dans **Modèles d'occupation**
2. Simuler avec ψ_vrai = 0.70, p = 0.35
3. Observer l'occupation observée (naïve)

**Question 1.1 :** L'occupation observée est environ 0.35 × 0.70 ≈ 0.25. Calculer le biais en % par rapport à ψ_vrai = 0.70.

### 1.2 Avec le modèle de MacKenzie

4. Ajuster le modèle d'occupation sur les mêmes données
5. Lire ψ estimé et p estimé avec leurs IC

**Question 1.2 :** Les estimations ψ̂ et p̂ sont-elles proches des valeurs simulées ? Quel est l'IC 95% de ψ ?

### 1.3 Nombre de visites

6. Réduire à 2 visites par placette, recalculer
7. Augmenter à 6 visites, recalculer

**Question 1.3 :** Quel est l'effet du nombre de visites sur la précision de l'estimation de ψ ? Quel compromis doit-on faire sur le terrain ?

### 1.4 Application pratique

**Question 1.4 :** Un suivi de 5 ans sans correction de détectabilité montre une occupation passant de 62% à 48%. Un suivi corrigé montre ψ stable à 0.70 mais p diminuant de 0.60 à 0.45. Comment interpréter cette divergence ?

---

## Partie 2 — Distance Sampling (30 min)

### Contexte
Des transects de 2 km sont réalisés pour estimer la densité de la Tourterelle des bois (*Streptopelia turtur*). 180 individus ont été détectés sur 15 km de transects cumulés. Les distances perpendiculaires varient de 0 à 150 m.

### 2.1 Ajuster la fonction de détection

1. Aller dans **Distance sampling**
2. Régler : n = 180, L = 15 km, distance max = 150 m
3. Choisir la fonction half-normal
4. Observer l'ajustement et l'AIC

5. Basculer sur hazard-rate
6. Comparer les AIC

**Question 2.1 :** Quelle fonction est retenue ? Quelle est la distance effective de détection (w̄) estimée ?

### 2.2 Estimer la densité

7. Lire la densité estimée D en individus/km²

**Question 2.2 :** La densité est D̂ = ? individus/km². Si la zone d'étude fait 150 km², quelle est l'abondance estimée ?

### 2.3 Précision

8. Observer le CV de l'estimation

**Question 2.3 :** CV = 18%. Est-ce une précision acceptable pour une décision de conservation ? Que faire pour réduire le CV ?

---

## Partie 3 — Séries temporelles et tendances (30 min)

### Contexte
Le Gobemouche gris (*Muscicapa striata*) est suivi par le programme STOC depuis 2000. Les comptages annuels montrent une apparente diminution.

### 3.1 Importer et visualiser

1. Aller dans **Séries temporelles**
2. Importer un CSV avec colonnes `annee` et `comptage` (ou utiliser les données simulées)
3. Observer la série brute avec les variations interannuelles

### 3.2 Test de Mann-Kendall

4. Appliquer le test de Mann-Kendall
5. Lire τ (tau de Kendall) et la p-value

**Question 3.1 :** τ = -0.38, p = 0.01. Quelle est la conclusion sur la tendance de la population ?

6. Lire la pente de Sen (individus perdus par an)

**Question 3.2 :** La pente de Sen est -3.2 individus/an sur une population initiale de 85 individus. En combien d'années la population sera-t-elle divisée par deux si la tendance se poursuit ?

### 3.3 Variabilité vs tendance

7. Augmenter la variabilité interannuelle (bruit) dans les données simulées
8. Observer l'effet sur la signification du test

**Question 3.3 :** Avec une forte variabilité, une tendance réelle de -2 individus/an peut être non détectée (p > 0.05). Combien d'années de suivi faut-il pour détecter une telle tendance avec 80% de puissance ?

---

## Partie 4 — PVA et Conservation (60 min)

### Contexte
Le Vautour moine (*Aegypius monachus*) est en cours de réintroduction. Paramètres issus de la littérature :
- N₀ = 35 individus reproducteurs
- r̄ = 0.04/an (légère croissance)
- σ = 0.18 (variabilité environnementale)
- K = 200 (capacité de charge estimée)
- Seuil de quasi-extinction = 15 individus
- Pertes annuelles = 3 (collisions avec lignes électriques)
- Horizon = 50 ans

### 4.1 Scénario de référence

1. Aller dans **PVA & Conservation**
2. Entrer les paramètres ci-dessus
3. Observer les trajectoires simulées (fanfare)
4. Lire le risque de quasi-extinction et la médiane de l'effectif final

**Question 4.1 :** Le risque de quasi-extinction est de ? %. La médiane finale est de ? individus. Le programme de réintroduction est-il viable à 50 ans sans intervention supplémentaire ?

### 4.2 Rôle de la stochasticité environnementale

5. Augmenter σ de 0.18 à 0.30 (années climatiques plus variables)
6. Observer l'effet sur le risque

**Question 4.2 :** Avec r̄ = 0.04 (positif), le risque augmente-t-il quand σ augmente ? Pourquoi un taux de croissance positif ne garantit-il pas la persistance ?

### 4.3 Éliminer les collisions

7. Revenir aux paramètres initiaux
8. Régler les pertes annuelles à 0 (programme de dépose des lignes à risque)
9. Comparer le risque au scénario de référence

**Question 4.3 :** Le risque passe de ?% à ?%. Quel est le bénéfice de l'élimination des collisions sur le risque de quasi-extinction ?

### 4.4 Renforcement de population

10. Conserver pertes = 3 mais augmenter N₀ à 70 (translocation de 35 individus supplémentaires)
11. Observer l'effet sur le risque et la médiane

**Question 4.4 :** Comparer l'efficacité de l'élimination des collisions vs le renforcement en termes de :
- Réduction du risque de quasi-extinction
- Coût probable (qualitatif)
- Durabilité à long terme

### 4.5 Aller dans **Scénarios de gestion**

12. Comparer les trois scénarios suivants en parallèle :
    - A : Référence (pas d'intervention)
    - B : Élimination des collisions (pertes = 0)
    - C : Restauration d'habitat (K = 350)
    - D : Renforcement + élimination (N₀ = 70, pertes = 0)

**Question 4.5 :** Classer ces scénarios par efficacité sur le risque de quasi-extinction. Quel scénario recommandez-vous et pourquoi ?

### 4.6 Incertitude sur les paramètres

**Question 4.6 :** Les paramètres r̄ et σ ont été estimés à partir de 8 ans de suivi seulement. Citez deux façons de prendre en compte cette incertitude dans la décision de conservation.

---

## Exercice intégrateur — Étude de cas complète (si temps disponible)

### Contexte
Vous êtes chargé de rédiger une note scientifique sur la viabilité de la population de Gypaète barbu (*Gypaetus barbatus*) dans les Pyrénées. Vous disposez de :
- 25 ans de données STOC
- Une estimation CMR (M = 40, C = 35, R = 12)
- Des paramètres démographiques issus de la littérature (matrice de Leslie)
- Des données GPS de 3 individus (domaine vital)

### Étapes

1. **Séries temporelles** : Analyser la tendance sur 25 ans → τ et pente
2. **CMR** : Estimer N̂ et l'IC
3. **Leslie** : Calculer λ avec les paramètres de la littérature
4. **PVA** : Simuler le risque de quasi-extinction à 50 ans
5. **Scénarios** : Comparer "sans intervention" vs "réduction de la mortalité juvénile"
6. **KDE** : Identifier les zones clés du domaine vital (50%)

**Production attendue :** Un PDF exporté depuis ORNI-LAB pour chaque module utilisé + une note d'interprétation de 300 mots.

---

## Questions de synthèse — Séance 4

**Question S4.1 :** Pour une espèce cryptique avec p = 0.3, l'occupation observée est 21% et ψ corrigé = 70%. Quelle est l'erreur commise si on utilise l'occupation naïve pour un rapport de conservation ?

**Question S4.2 :** La PVA donne un risque de 8% avec σ = 0.10 et un risque de 42% avec σ = 0.30. Le biologiste de terrain préfère travailler avec σ = 0.10 car "les données récentes sont bonnes". Que lui répondez-vous ?

**Question S4.3 :** Vous n'avez que 3 ans de données pour la PVA au lieu de 10. Comment adaptez-vous votre analyse et votre discours aux décideurs ?

**Question S4.4 :** Un décideur demande "combien d'années avant l'extinction ?" Comment répondez-vous à partir d'une PVA ?

---

## Récapitulatif du cursus — Les 18 modules et leurs usages

| Module | Quand l'utiliser | Donnée nécessaire |
|--------|-----------------|-------------------|
| Analyse CSV | Premiers pas avec un fichier terrain | Fichier CSV |
| Statistiques descriptives | Résumer une variable | Aucune (simulation) |
| Corrélation & régression | Relation entre 2 variables | Aucune (simulation) |
| Tests statistiques | Comparer 2-3 groupes | Aucune (simulation) |
| GLM Comptage | Modéliser des abondances | Aucune (simulation) |
| Modèles mixtes | Données groupées | Aucune (simulation) |
| Domaine vital MCP | Domaine vital géométrique | Coordonnées GPS |
| Domaine vital KDE | Domaine vital probabiliste | Coordonnées GPS |
| Richesse & Diversité | Comparer des communautés | Liste d'espèces + abondances |
| Croissance | Projeter N dans le temps | Aucune (simulation) |
| Matrices de Leslie | Dynamique structurée | Fécondités + survies par classe |
| CMR | Estimer une population difficile | M, C, R |
| Modèles d'occupation | Occupation + détectabilité | Données de visites répétées |
| Distance sampling | Densité sur transects | Distances de détection |
| Lotka-Volterra | Dynamique proie-prédateur | Aucune (simulation) |
| Séries temporelles | Tendance sur plusieurs années | CSV annee + comptage |
| PVA | Risque de quasi-extinction | N₀, r, σ, K, seuil |
| Scénarios de gestion | Comparer des actions | Paramètres PVA |
