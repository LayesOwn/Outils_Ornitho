# Fiches pédagogiques — Section Dynamique des populations

> Dix fiches, une par module. Chaque fiche contient : objectif, concept clé, manipulation guidée, questions d'interprétation, erreurs fréquentes.

---

## Fiche 9 — Richesse & Diversité

### Objectif pédagogique
Calculer et comparer des indices de diversité entre communautés. Comprendre ce que chaque indice mesure réellement.

### Concept clé

| Indice | Ce qu'il mesure | Sensible aux espèces rares ? |
|--------|----------------|------------------------------|
| Richesse spécifique (S) | Nombre d'espèces | Oui (chaque espèce compte pareil) |
| Shannon (H') | Diversité + équitabilité | Modérément |
| Simpson (1-D) | Dominance inversée | Non (pondère par abondance) |
| Équitabilité (J) | Régularité des abondances | — |

### Manipulation guidée

**Étape 1 — Simuler deux communautés**
1. Communauté A : 5 espèces avec abondances égales (20, 20, 20, 20, 20)
2. Communauté B : 5 espèces avec dominance (80, 5, 5, 5, 5)
3. Comparer S, H', Simpson, J

**Étape 2 — Courbe d'accumulation**
1. Régler l'effort d'échantillonnage (nombre de sites/points)
2. Observer à partir de quel effort la richesse se stabilise
3. Interpréter l'asymptote comme la richesse estimée du peuplement

**Étape 3 — Comparer deux habitats**
1. Charger deux jeux de données (ou simuler)
2. Comparer les indices et les courbes d'accumulation

### Questions d'interprétation

1. Deux forêts ont H' = 2.1 et H' = 2.3. La différence est-elle biologiquement significative ?
2. Une forêt a S = 20, H' = 1.2 ; une prairie a S = 15, H' = 2.8. Laquelle est "plus diverse" ?
3. La courbe d'accumulation n'atteint pas l'asymptote après 40 points d'écoute. Que cela suggère-t-il sur l'effort ?
4. L'équitabilité J = 0.95 signifie quoi sur la structure du peuplement ?

### Erreurs fréquentes

- Comparer des richesses mesurées avec des efforts d'échantillonnage différents
- Utiliser Shannon sans préciser la base du logarithme (nat, bits, décits)
- Conclure qu'une communauté est "meilleure" car H' est plus élevé

---

## Fiche 10 — Croissance exponentielle et logistique

### Objectif pédagogique
Comprendre les deux régimes de croissance d'une population. Visualiser l'effet de la capacité de charge K.

### Concept clé

| Modèle | Équation | Hypothèse |
|--------|----------|-----------|
| Exponentiel | dN/dt = rN | Pas de limite de ressources |
| Logistique | dN/dt = rN(1 - N/K) | Ralentissement quand N → K |

Le paramètre r intègre : naissances, morts, immigration, émigration.

### Manipulation guidée

**Étape 1 — Croissance libre**
1. Régler N₀ = 50, r = 0.15, K = 500, horizon = 30 ans
2. Observer la courbe exponentielle (sans limite)
3. Augmenter r → la courbe monte plus vite

**Étape 2 — Effet de K**
1. Activer le modèle logistique
2. Observer la stabilisation vers K
3. Réduire K de moitié (simuler perte d'habitat)
4. Observer la population atteindre une nouvelle asymptote plus basse

**Étape 3 — Scénarios de départ**
1. N₀ > K → la population décline vers K
2. N₀ = K/2 → croissance maximale (inflexion de la courbe)
3. N₀ très faible + r faible → risque d'extinction si bruit ajouté

### Questions d'interprétation

1. r = -0.05. Que se passe-t-il à long terme, indépendamment de K ?
2. Doubler K de 200 à 400 : la population à l'an 20 double-t-elle également ?
3. La courbe logistique passe par son point d'inflexion à N = K/2. À quel moment la croissance nette est-elle maximale ?
4. En quoi ce modèle est-il insuffisant pour modéliser une espèce migratrice ?

### Erreurs fréquentes

- Confondre r (taux intrinsèque) et λ (taux de croissance discret λ = e^r)
- Croire que N > K est impossible (il est temporaire mais biologiquement possible)
- Ignorer que K peut changer avec le temps (changement climatique, urbanisation)

---

## Fiche 11 — Matrices de Leslie

### Objectif pédagogique
Projeter la dynamique d'une population structurée par classes d'âge. Identifier quel paramètre (fécondité ou survie) pilote le plus la croissance.

### Concept clé

La matrice de Leslie organise les transitions entre classes d'âge :
```
L = | F₀  F₁  F₂  |    Fᵢ = fécondité de la classe i
    | S₀  0   0   |    Sᵢ = survie de la classe i (passage à i+1)
    | 0   S₁  0   |
```

**λ (lambda)** : valeur propre dominante
- λ > 1 → croissance
- λ = 1 → stabilité
- λ < 1 → déclin

### Manipulation guidée

**Étape 1 — Paramétrer la matrice**
1. Choisir 3 classes d'âge (juvénile, subadulte, adulte)
2. Régler les fécondités : F₀ = 0, F₁ = 0.5, F₂ = 1.2
3. Régler les survies : S₀ = 0.4, S₁ = 0.7, S₂ = 0.85
4. Observer λ calculé

**Étape 2 — Sensibilité vs élasticité**
1. Observer le tableau de sensibilité (dérivée de λ par rapport à chaque paramètre)
2. Observer le tableau d'élasticité (variation proportionnelle)
3. Identifier quel paramètre a l'élasticité la plus haute

**Étape 3 — Scénario de conservation**
1. Améliorer la survie adulte de 5% → recalculer λ
2. Améliorer la fécondité de 20% → recalculer λ
3. Comparer l'impact des deux interventions

### Questions d'interprétation

1. λ = 0.93. Combien de temps avant que la population soit réduite de moitié (approximation) ?
2. L'élasticité de S₂ (survie adulte) est 0.48 et celle de F₂ (fécondité adulte) est 0.12. Quelle intervention de conservation est prioritaire ?
3. La structure initiale est fortement biaisée vers les adultes. La dynamique à court terme sera-t-elle différente de la dynamique asymptotique ?
4. Pourquoi les matrices de Leslie supposent-elles des paramètres constants d'une année à l'autre ?

### Erreurs fréquentes

- Confondre λ (taux discret) et r (taux continu)
- Interpréter la dynamique transitoire comme la tendance à long terme
- Utiliser une matrice avec trop peu de données pour calibrer les paramètres

---

## Fiche 12 — Capture-Marquage-Recapture (CMR)

### Objectif pédagogique
Estimer l'effectif d'une population à partir de sessions de capture. Comprendre les hypothèses et leur impact sur la validité de l'estimation.

### Concept clé — Estimateur de Lincoln-Petersen

```
N̂ = (M × C) / R

M = nombre d'individus marqués lors de la 1ère session
C = nombre d'individus capturés lors de la 2ème session
R = nombre d'individus marqués recapturés à la 2ème session
```

L'intervalle de confiance à 95% dépend directement de R : plus R est faible, plus l'incertitude est grande.

### Hypothèses à respecter

1. Population fermée entre les deux sessions (pas de naissances, morts, immigration, émigration)
2. Les marques sont conservées et reconnues
3. Probabilité de capture identique pour tous les individus
4. Mélange homogène des individus marqués et non marqués

### Manipulation guidée

**Étape 1 — Scénario de base**
1. M = 50, C = 40, R = 20 → calculer N̂ et l'IC 95%
2. Observer l'étendue de l'intervalle de confiance

**Étape 2 — Effet de R**
1. Conserver M = 50, C = 40
2. Faire varier R de 5 à 35
3. Observer comment N̂ et l'IC varient

**Étape 3 — Violation des hypothèses**
1. Que se passe-t-il si des individus marqués évitent les pièges (comportement de piège) ?
2. Et si la population n'est pas fermée (émigration entre sessions) ?

### Questions d'interprétation

1. M = 100, C = 80, R = 8. Calculer N̂ à la main. Quel est le taux de recapture ? Est-il suffisant ?
2. L'IC 95% est [450 – 2100]. Peut-on prendre une décision de gestion avec cette précision ?
3. Comment améliorer la précision de l'estimation sans augmenter l'effort de capture ?
4. Pour quelle raison les oiseaux chanteurs nicheurs sont-ils une bonne cible pour la CMR ?

### Erreurs fréquentes

- Utiliser Lincoln-Petersen quand la population n'est clairement pas fermée
- Sous-estimer N quand les individus marqués sont plus facilement capturés (comportement de piège positif)
- Confondre taux de recapture (R/C) et taux de survie annuel

---

## Fiche 13 — Modèles d'occupation

### Objectif pédagogique
Estimer la probabilité d'occupation d'un habitat en tenant compte d'une détectabilité imparfaite.

### Concept clé
Un site peut être occupé mais l'espèce non détectée lors d'une visite (faux-négatif). Sans correction, l'occupation estimée est systématiquement sous-estimée.

```
Occupation observée = Occupation réelle × Probabilité de détection
ψ_observée = ψ × p
```

Le modèle de MacKenzie estime séparément ψ (occupation) et p (détectabilité) à partir de données de visites répétées.

### Manipulation guidée

**Étape 1 — Sans correction de détectabilité**
1. Simuler des données avec ψ = 0.7 et p = 0.4
2. Observer que l'occupation observée ≈ 0.28 (= 0.7 × 0.4)
3. Mesurer le biais

**Étape 2 — Avec le modèle d'occupation**
1. Ajuster le modèle sur les mêmes données
2. Observer les estimations de ψ et p
3. Comparer avec les valeurs simulées

**Étape 3 — Nombre de visites**
1. Répéter avec 2, 3, 5 visites par site
2. Observer la réduction de l'intervalle de confiance sur ψ

### Questions d'interprétation

1. ψ = 0.65 (IC : 0.52–0.78) et p = 0.35. Combien de visites sont nécessaires pour détecter une espèce présente avec 95% de certitude ?
2. Si p varie selon la saison, que se passe-t-il si on mélange des visites printanières et automnales ?
3. Un gestionnaire a des données d'occupation sur 5 ans sans correction de détectabilité. Pourquoi la tendance peut-elle être biaisée ?
4. Quel est le nombre minimal de visites répétées recommandé pour que le modèle converge ?

### Erreurs fréquentes

- Utiliser l'occupation observée sans corriger pour p (sous-estimation systématique)
- Trop peu de visites répétées (< 3) : le modèle ne peut pas séparer ψ et p
- Ignorer que p peut varier selon la météo, la saison ou l'observateur

---

## Fiche 14 — Distance Sampling

### Objectif pédagogique
Estimer la densité d'une espèce sur des transects en tenant compte de la décroissance de la détectabilité avec la distance.

### Concept clé
La probabilité de détecter un individu diminue avec la distance au transect. En modélisant cette relation (fonction de détection), on peut estimer la densité réelle.

```
D = n / (2 × L × w̄)

D = densité estimée
n = nombre d'individus détectés
L = longueur totale des transects
w̄ = distance effective de détection (intégrale de la fonction de détection)
```

### Fonctions de détection disponibles

| Fonction | Forme | Cas d'usage |
|----------|-------|------------|
| Half-normal | Décroissance douce | Espèces à détectabilité progressive |
| Hazard-rate | Plateau puis chute abrupte | Espèces avec "épaule" de détection |

### Manipulation guidée

**Étape 1 — Simuler un transect**
1. Régler la densité vraie (ex. : 5 individus/ha)
2. Régler la distance maximale de détection et le paramètre de décroissance
3. Observer le nuage de distances observées

**Étape 2 — Ajuster la fonction de détection**
1. Choisir la fonction half-normal
2. Observer l'ajustement au nuage de points
3. Comparer l'AIC avec la fonction hazard-rate

**Étape 3 — Interprétation**
1. Lire la densité estimée et son CV
2. Comparer avec la densité vraie simulée
3. Augmenter n (plus de détections) → observer la réduction du CV

### Questions d'interprétation

1. La densité estimée est 4.8 individus/ha, densité vraie = 5. Le biais est de quel ordre ?
2. Le CV est de 28%. Cet estimateur est-il précis pour une décision de gestion ?
3. Pourquoi est-il important que les individus soient détectés à leur position initiale (avant flush) ?
4. Quel est l'impact d'un observateur qui tend à sur-enregistrer les individus proches du transect ?

### Erreurs fréquentes

- Grouper à des distances non appropriées (trop large → perdre la structure de décroissance)
- Comparer des densités estimées sur des transects de longueur très différente sans normalisation
- Appliquer le distance sampling à des espèces très cryptiques sans vérification préalable

---

## Fiche 15 — Lotka-Volterra

### Objectif pédagogique
Explorer la dynamique proie-prédateur et comprendre les conditions d'oscillations, d'équilibre ou d'extinction.

### Concept clé

```
dV/dt = αV - βVP     (Proies : croissance naturelle - prédation)
dP/dt = δVP - γP     (Prédateurs : gains par prédation - mortalité)

α = taux de croissance des proies
β = taux de prédation
δ = efficacité de conversion (proies → prédateurs)
γ = taux de mortalité des prédateurs
```

**Point d'équilibre :** V* = γ/δ, P* = α/β

### Manipulation guidée

**Étape 1 — Oscillations de base**
1. Régler α = 0.4, β = 0.02, δ = 0.01, γ = 0.3
2. Observer les oscillations déphasées (proies en avance sur prédateurs)
3. Observer le portrait de phase (cycle fermé)

**Étape 2 — Modifier les paramètres**
1. Augmenter β (prédation plus efficace) → oscillations plus prononcées
2. Augmenter γ (mortalité des prédateurs) → proies plus abondantes à l'équilibre
3. Modifier les effectifs initiaux → changer l'amplitude des oscillations

**Étape 3 — Cas limites**
1. δ très faible → les prédateurs ne peuvent pas soutenir leur population
2. Proies initiales très faibles → risque d'extinction en chaîne

### Questions d'interprétation

1. Le décalage entre le pic des proies et le pic des prédateurs est d'environ 1/4 de cycle. Pourquoi ce délai ?
2. Augmenter α (taux de croissance des proies) augmente-t-il ou diminue-t-il l'effectif moyen des prédateurs ?
3. Ce modèle prédit des oscillations éternelles. Pourquoi n'observe-t-on pas cela dans la nature ?
4. Donner un exemple réel de couple proie-prédateur dans les oiseaux.

### Erreurs fréquentes

- Croire que les oscillations sont stables indépendamment des perturbations (elles sont structurellement neutres)
- Oublier que le modèle n'a pas de capacité de charge pour les proies
- Interpréter un équilibre comme stable alors qu'il est neutre (tout choc change l'amplitude)

---

## Fiche 16 — Séries temporelles

### Objectif pédagogique
Détecter et quantifier une tendance annuelle dans des comptages d'oiseaux sur plusieurs années.

### Concept clé

| Méthode | Hypothèse | Usage |
|---------|-----------|-------|
| **Mann-Kendall** | Non-paramétrique, monotone | Tendance sans supposer normalité |
| **Sen's slope** | Non-paramétrique | Magnitude de la tendance |
| **Régression linéaire** | Paramétrique | Tendance linéaire supposée |

Le test de Mann-Kendall teste H₀ : "pas de tendance monotone" → τ (tau) de Kendall et p-value.

### Manipulation guidée

**Étape 1 — Tendance positive**
1. Simuler une série avec tendance croissante modérée + bruit
2. Observer τ positif et p-value faible
3. Lire la pente estimée (changement par an)

**Étape 2 — Bruit vs tendance**
1. Augmenter la variabilité interannuelle (bruit)
2. Observer que la tendance peut ne plus être détectable statistiquement
3. Comprendre la notion de puissance statistique

**Étape 3 — Données réelles**
1. Importer un CSV avec colonnes Année et Comptage
2. Appliquer Mann-Kendall
3. Interpréter le résultat pour une décision de suivi

### Questions d'interprétation

1. τ = -0.42, p = 0.003. Que conclut-on sur la tendance de cette espèce ?
2. La pente est de -2.3 individus/an sur une population de 80 individus. En combien d'années la population est-elle divisée par deux ?
3. Les résultats varient selon la période choisie (1990-2010 vs 2000-2020). Que cela indique-t-il ?
4. Pourquoi Mann-Kendall est-il préférable à une régression linéaire pour des comptages annuels ?

### Erreurs fréquentes

- Choisir la période d'analyse pour que le résultat soit significatif (p-hacking)
- Conclure à une absence de tendance si p > 0.05 avec peu d'années (< 10)
- Ignorer les ruptures de protocole de comptage dans la série

---

## Fiche 17 — PVA & Conservation

### Objectif pédagogique
Évaluer la viabilité à long terme d'une population en simulant l'incertitude démographique et environnementale.

### Concept clé
La PVA (Population Viability Analysis) simule de nombreuses trajectoires stochastiques (≈ 250 ici) avec variation aléatoire de r chaque année. Elle calcule la proportion de trajectoires qui passent sous un seuil de quasi-extinction.

**Paramètres clés :**

| Paramètre | Rôle |
|-----------|------|
| N₀ | Effectif initial |
| r̄ | Tendance moyenne (positif = croissance) |
| σ (sd_r) | Stochasticité environnementale |
| K | Capacité de charge (plafond) |
| Seuil | Effectif critique sous lequel = quasi-extinction |
| Pertes annuelles | Mortalité additive (collision, prélèvement, etc.) |
| Horizon | Durée de projection |

### Manipulation guidée

**Étape 1 — Scénario de base**
1. N₀ = 100, r = 0.02, σ = 0.15, K = 500, seuil = 20, pertes = 0, horizon = 50 ans
2. Observer le risque de quasi-extinction et la médiane de l'effectif final
3. Observer la dispersion des trajectoires (fanfare)

**Étape 2 — Rôle de la variance**
1. Conserver r = 0.02 (croissance positive)
2. Augmenter σ de 0.05 à 0.30
3. Observer que le risque peut augmenter même avec r positif

**Étape 3 — Pertes annuelles**
1. Ajouter pertes = 5 individus/an
2. Observer l'effet sur le risque et la médiane finale
3. Réduire les pertes → mesure de conservation

**Étape 4 — Sensibilité au seuil**
1. Changer le seuil de 10 à 50
2. Observer l'augmentation mécanique du risque

### Questions d'interprétation

1. Risque = 12% sur 50 ans. Que signifie ce chiffre pour un gestionnaire ?
2. Avec r = 0.03 et σ = 0.25, le risque est de 35%. Avec r = 0.00 et σ = 0.05, il est de 15%. Quelle population est plus vulnérable ?
3. La PVA simplifie beaucoup la réalité. Citer 3 facteurs non représentés dans ce modèle.
4. Comment utiliser les résultats de la PVA pour justifier une mesure de conservation ?

### Erreurs fréquentes

- Interpréter le risque comme une probabilité exacte d'extinction à une date précise
- Croire qu'un r positif garantit la persistance (la variance peut dominer)
- Oublier que le seuil de quasi-extinction est une décision arbitraire du modélisateur

---

## Fiche 18 — Scénarios de gestion

### Objectif pédagogique
Comparer l'efficacité relative de différentes actions de conservation sur une population menacée. Justifier scientifiquement une décision de gestion.

### Concept clé
Trois types d'actions modélisables :
- **Restauration d'habitat** → augmenter K
- **Réduction de la mortalité** → diminuer les pertes annuelles
- **Translocation** → augmenter N₀

La comparaison porte sur le risque de quasi-extinction final et la médiane de l'effectif projeté.

### Manipulation guidée

**Étape 1 — Définir le scénario de référence**
1. Régler les paramètres de base (N₀ faible, risque élevé)
2. Enregistrer le risque de référence

**Étape 2 — Comparer les actions**
1. Scénario A : restauration d'habitat (K × 2)
2. Scénario B : réduction des collisions (pertes → 0)
3. Scénario C : translocation (N₀ + 50)
4. Comparer les risques et les médianes finales sur un graphique

**Étape 3 — Action combinée**
1. Combiner restauration + réduction de mortalité
2. Observer si l'effet est additif ou synergique
3. Discuter du coût-efficacité de chaque action

### Questions d'interprétation

1. La restauration d'habitat réduit le risque de 42% à 18%. La translocation le réduit de 42% à 35%. Quelle action recommandez-vous et pourquoi ?
2. Une action est efficace dans le modèle mais très coûteuse en pratique. Comment intégrer cette contrainte dans la décision ?
3. Pourquoi comparer les médianes finales en plus du risque de quasi-extinction ?
4. Le modèle suppose que les paramètres des scénarios sont connus avec certitude. Que faire si les données sont insuffisantes pour estimer K ou les pertes annuelles ?

### Erreurs fréquentes

- Choisir l'action qui minimise le risque sans considérer la faisabilité terrain
- Oublier que les hypothèses du scénario (ex. : l'habitat restauré est réellement colonisé) doivent être vérifiées
- Comparer des scénarios avec des horizons temporels différents

---

## Récapitulatif Dynamique des populations

### Choisir la bonne méthode

| Question biologique | Module recommandé |
|--------------------|-----------------|
| Comparer des communautés | Richesse & diversité |
| Projeter N à t+50 ans | Croissance exponentielle/logistique |
| Quelle classe d'âge protéger ? | Matrices de Leslie |
| Combien d'individus dans cette population ? | CMR |
| L'espèce occupe-t-elle ce site ? | Modèles d'occupation |
| Quelle densité sur mes transects ? | Distance sampling |
| Proie-prédateur : oscillations | Lotka-Volterra |
| Tendance sur 20 ans de comptages | Séries temporelles |
| Risque d'extinction à 50 ans ? | PVA & Conservation |
| Quelle action de conservation prioriser ? | Scénarios de gestion |

### Progression recommandée

```
Niveau 1 (débutant)
  → Croissance logistique
  → CMR
  → Richesse & diversité

Niveau 2 (intermédiaire)
  → Matrices de Leslie
  → Modèles d'occupation
  → Séries temporelles

Niveau 3 (avancé)
  → PVA & conservation
  → Scénarios de gestion
  → Distance sampling
  → Lotka-Volterra
```
