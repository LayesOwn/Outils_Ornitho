# TP Séance 3 — Dynamique des populations (fondamentaux)

**Durée :** 3 heures | **Public :** L3/Master | **Prérequis :** Séances 1 et 2

**Objectifs :**
- Calculer et comparer des indices de diversité
- Simuler la croissance exponentielle et logistique
- Construire et interpréter une matrice de Leslie
- Estimer l'effectif d'une population par capture-marquage-recapture

---

## Partie 1 — Richesse & Diversité (30 min)

### Contexte
On compare les communautés d'oiseaux nicheurs dans trois types d'habitats d'une réserve naturelle : roselière, prairie humide, boisement alluvial.

### 1.1 Indices de base

1. Aller dans **Richesse & Diversité**
2. Simuler trois communautés avec les profils suivants :

| Communauté | Description | Richesse S |
|------------|-------------|-----------|
| Roselière | Forte dominance (Rousserolle effarvatte >> autres) | 12 espèces |
| Prairie humide | Distribution équilibrée | 15 espèces |
| Boisement | Quelques espèces forestières abondantes | 18 espèces |

3. Calculer H' (Shannon), Simpson (1-D), et J (équitabilité) pour chaque communauté

**Question 1.1 :** Le boisement a la plus grande richesse (S = 18) mais est-il le plus "divers" selon H' ? Expliquer.

**Question 1.2 :** Quelle communauté a le J (équitabilité) le plus proche de 1 ? Que signifie biologiquement J ≈ 1 ?

### 1.2 Courbes d'accumulation

4. Pour chaque communauté, tracer la courbe d'accumulation (richesse en fonction de l'effort)
5. Observer où se situe l'asymptote

**Question 1.3 :** Après 20 points d'écoute, la courbe de la prairie n'atteint pas l'asymptote. Quel protocole recommandez-vous pour estimer la richesse réelle ?

---

## Partie 2 — Croissance exponentielle et logistique (45 min)

### Contexte
La population de Milan royal (*Milvus milvus*) sur un site de réintroduction est suivie depuis l'an 0. Paramètres estimés : N₀ = 10 couples, r = 0.12/an, K estimée à 80 couples.

### 2.1 Croissance libre

1. Aller dans **Croissance exponentielle/logistique**
2. Régler : N₀ = 10, r = 0.12, K = 80, horizon = 30 ans
3. Observer la courbe exponentielle (sans limite)

**Question 2.1 :** Après 30 ans, à combien de couples la croissance exponentielle prévoit-elle d'arriver ? Est-ce réaliste ?

### 2.2 Croissance logistique

4. Activer le modèle logistique (avec K)
5. Observer la courbe en S

**Question 2.2 :** À quel moment la croissance annuelle nette est-elle maximale ? Pourquoi ce point correspond-il à N = K/2 = 40 couples ?

### 2.3 Perte d'habitat

6. Réduire K de 80 à 40 (perte de 50% de l'habitat favorable)
7. Observer la nouvelle trajectoire

**Question 2.3 :** La population se stabilise maintenant à 40 couples. En combien d'années atteint-elle 90% de la nouvelle capacité de charge ?

### 2.4 Déclin

8. Régler r = -0.08 (déclin, ex. : persécution, empoisonnement)
9. Observer la trajectoire à partir de N₀ = 60 couples

**Question 2.4 :** Avec r = -0.08, la population est réduite de moitié en environ combien d'années ? (Utiliser T₁/₂ ≈ ln(2)/|r|)

### 2.5 Rôle de r

10. Tester r = 0, r = 0.05, r = 0.12, r = 0.20 avec les mêmes N₀ et K
11. Comparer les trajectoires

**Question 2.5 :** Quelle est la différence de population à l'an 20 entre r = 0.05 et r = 0.20 ? Quelle intervention de conservation permettrait d'augmenter r ?

---

## Partie 3 — Matrices de Leslie (60 min)

### Contexte
La Cigogne blanche (*Ciconia ciconia*) a 3 classes d'âge : Juvéniles (0-1 an), Subadultes (1-2 ans), Adultes (≥ 2 ans).

Paramètres estimés :
- F₀ = 0 (les juvéniles ne se reproduisent pas)
- F₁ = 0.3 (jeunes femelles/subadulte)
- F₂ = 0.9 (jeunes femelles/adulte)
- S₀ = 0.45 (survie juvénile)
- S₁ = 0.72 (survie subadulte)
- S₂ = 0.85 (survie adulte)

Structure initiale : 40 juvéniles, 20 subadultes, 50 adultes

### 3.1 Construire la matrice

1. Aller dans **Matrices de Leslie**
2. Entrer les paramètres ci-dessus
3. Observer la matrice construite

**Question 3.1 :** Écrire la matrice de Leslie 3×3 avec ces valeurs.

### 3.2 Calculer λ

4. Lancer la projection
5. Lire λ dominant

**Question 3.2 :** λ = ? La population est-elle en croissance, stable ou en déclin asymptotique ?

### 3.3 Distribution stable des âges

6. Projeter sur 30 ans
7. Observer la convergence vers la structure stable des âges

**Question 3.3 :** Quelle proportion de la population est constituée d'adultes à la structure stable ? Est-ce cohérent avec une population longévive comme la Cigogne ?

### 3.4 Sensibilité et élasticité

8. Observer le tableau de sensibilité et d'élasticité
9. Identifier le paramètre avec l'élasticité la plus haute

**Question 3.4 :** Si l'élasticité de S₂ est 0.52 et celle de F₂ est 0.18, quelle intervention a le plus d'impact sur λ : améliorer la survie adulte de 5% ou doubler la fécondité adulte ?

### 3.5 Scénario de conservation

10. Augmenter S₀ de 0.45 à 0.60 (programme de renforcement des juvéniles)
11. Recalculer λ

12. Augmenter S₂ de 0.85 à 0.90 (réduction de la mortalité par collision)
13. Recalculer λ

**Question 3.5 :** Quelle intervention est la plus efficace pour améliorer λ ? Ce résultat est-il cohérent avec l'analyse d'élasticité ?

### 3.6 Structure initiale non stable

14. Changer la structure initiale : 10 juvéniles, 5 subadultes, 85 adultes (population vieillie)
15. Observer la trajectoire sur 5 ans vs 20 ans

**Question 3.6 :** Une population vieillie peut-elle temporairement avoir λ_observé > λ_asymptotique ? Pourquoi ?

---

## Partie 4 — Capture-Marquage-Recapture (30 min)

### Contexte
Une étude CMR est menée sur le Bruant des roseaux (*Emberiza schoeniclus*) dans une roselière. Session 1 (mars) : 60 individus bagués. Session 2 (avril, même année) : 45 individus capturés, dont 18 portent des bagues.

### 4.1 Estimation de Lincoln-Petersen

1. Aller dans **CMR**
2. Entrer M = 60, C = 45, R = 18
3. Lire N̂ et l'IC 95%

**Question 4.1 :** 
- Calculer N̂ à la main (N̂ = M×C/R)
- Comparer avec le résultat d'ORNI-LAB
- L'IC 95% est-il large ou étroit ? Que cela implique-t-il ?

### 4.2 Sensibilité à R

4. Conserver M = 60, C = 45
5. Faire varier R de 5 à 40 (pas de 5)
6. Observer comment N̂ et l'IC évoluent

**Question 4.2 :** À partir de quel R l'IC devient-il suffisamment précis (largeur < 2× la valeur estimée) ?

### 4.3 Violations des hypothèses

**Question 4.3 :** Pour chaque situation, dire si l'estimation sera biaisée (surestimée ou sous-estimée) et pourquoi :
- a) Des bagues tombent entre les deux sessions
- b) Les individus bagués deviennent plus méfiants (piège-timidité)
- c) 10% des individus ont migré entre les deux sessions

### 4.4 Planification d'une étude

**Question 4.4 :** Vous planifiez une CMR pour estimer une population de 300 individus avec un CV inférieur à 20%. Combien d'individus devez-vous marquer lors de la session 1 si vous prévoyez de capturer 80 individus lors de la session 2 ?

---

## Questions de synthèse — Séance 3

**Question S3.1 :** Une population de Rollier d'Europe est suivie avec une matrice de Leslie (λ = 0.96) et une CMR (N̂ = 420 individus). Comment combiner ces deux informations pour évaluer l'urgence d'une mesure de conservation ?

**Question S3.2 :** La courbe de croissance logistique suppose K constant. Citez deux perturbations écologiques récentes susceptibles de modifier K pour une espèce de prairie.

**Question S3.3 :** Compléter le tableau avec la méthode la mieux adaptée :

| Objectif | Méthode |
|----------|---------|
| Estimer N dans une colonie de Hérons | ? |
| Projeter la population sur 20 ans avec structure d'âge | ? |
| Identifier si le site a une diversité en déclin | ? |
| Modéliser la stabilisation vers la capacité de charge | ? |

---

## Pour aller plus loin

- Mode Enseignant dans Matrices de Leslie : voir la décomposition spectrale et les formules d'élasticité
- Lire le guide scientifique sur les Matrices de Leslie et le CMR
- Comparer les résultats Leslie avec une PVA stochastique (Séance 4)
- Explorer les données STOC (Suivi Temporel des Oiseaux Communs) pour calibrer une matrice de Leslie réaliste
