# TP Séance 2 — Biostatistiques avancées

**Durée :** 3 heures | **Public :** L3/Master | **Prérequis :** Séance 1

**Objectifs :**
- Choisir le bon test statistique selon la structure des données
- Modéliser des comptages avec un GLM Poisson ou binomial négatif
- Comprendre l'intérêt des modèles mixtes pour les données groupées
- Calculer et interpréter un domaine vital (MCP et KDE)

---

## Partie 1 — Tests statistiques (45 min)

### Contexte
On compare le succès reproducteur (nombre de jeunes à l'envol) de la Chouette hulotte (*Strix aluco*) dans deux types de forêts : feuillue vs résineuse. Des données simulées sont disponibles dans le module.

### 1.1 t-test de Welch

1. Aller dans **Tests statistiques**
2. Simuler deux groupes : n_feuillue = 25, n_résineuse = 25
3. Régler les moyennes : feuillue = 2.8 jeunes, résineuse = 2.1 jeunes
4. Régler une variabilité modérée

**Question 1.1 :** La différence est-elle statistiquement significative ? Quelle est la taille de l'effet (différence de moyennes / écart-type) ?

5. Réduire les effectifs à n = 8 par groupe, garder les mêmes moyennes
6. Observer le changement de la p-value

**Question 1.2 :** La différence biologique est identique mais la conclusion statistique change. Que cela illustre-t-il sur la puissance d'un test ?

### 1.2 Mann-Whitney (non-paramétrique)

7. Simuler une distribution très asymétrique (quelques nids très productifs)
8. Comparer t-test vs Mann-Whitney

**Question 1.3 :** Dans quel cas préférer Mann-Whitney au t-test de Welch ?

### 1.3 ANOVA

9. Passer à 3 groupes (feuillue, résineuse, mixte)
10. Observer le F de Fisher et la p-value globale
11. Identifier quelle paire de groupes est différente

**Question 1.4 :** L'ANOVA globale est significative (p = 0.02) mais la comparaison résineuse vs mixte ne l'est pas (p = 0.38). Comment interpréter ces deux résultats ensemble ?

---

## Partie 2 — GLM Comptage (45 min)

### Contexte
On modélise l'abondance du Bruant proyer (*Emberiza calandra*) sur 60 placettes en fonction du type d'habitat (prairie intensive vs extensive) et de la présence de haies.

### 2.1 Distribution des comptages

1. Aller dans **GLM Comptage**
2. Simuler des comptages avec faible surdispersion
3. Observer la distribution : est-elle compatible avec une loi normale ?

**Question 2.1 :** Pourquoi ne peut-on pas utiliser directement une régression linéaire sur des comptages d'oiseaux ?

### 2.2 Poisson vs Binomial négatif

4. Ajuster un GLM Poisson
5. Observer le ratio déviance résiduelle / degrés de liberté

**Question 2.2 :** Le ratio est de 3.4. Qu'est-ce que cela indique sur la qualité du modèle Poisson ?

6. Basculer sur le modèle Binomial négatif
7. Comparer les AIC des deux modèles

**Question 2.3 :** Lequel des deux modèles est préférable ici ? Par combien de points d'AIC ?

### 2.3 Interpréter les coefficients

8. Observer les coefficients β du modèle retenu
9. Calculer exp(β_habitat) pour obtenir le ratio d'abondance

**Exemple :** Si β_prairie_extensive = 0.85 → exp(0.85) ≈ 2.34
→ L'abondance est 2.34 fois plus élevée en prairie extensive qu'en prairie intensive

**Question 2.4 :** β_haie = 0.62. Calculer et interpréter l'effet de la présence de haies sur l'abondance du Bruant proyer.

### 2.4 Prédictions

10. Utiliser le modèle pour prédire l'abondance dans une prairie extensive avec haies
11. Comparer avec l'observation moyenne correspondante

---

## Partie 3 — Modèles mixtes LMM (45 min)

### Contexte
On mesure la longueur de tarse de jeunes Mésanges bleues (*Cyanistes caeruleus*) dans 8 nichoirs répartis sur 4 sites. Plusieurs poussins par nichoir sont mesurés. Les poussins du même nichoir ne sont pas indépendants.

### 3.1 Visualiser la structure hiérarchique

1. Aller dans **Modèle mixte**
2. Paramétrer : 8 nichoirs (groupes), 5 mesures par nichoir
3. Observer la variabilité inter-nichoirs vs intra-nichoir

**Question 3.1 :** L'ICC est de 0.55. Que signifie ce chiffre pour la structure des données ?

### 3.2 Comparer modèle simple vs mixte

4. Ajuster une régression simple sans effet groupe
5. Ajuster un modèle mixte avec nichoir comme effet aléatoire
6. Comparer les erreurs standards des coefficients fixes

**Question 3.2 :** L'erreur standard de l'effet "qualité du site" est plus grande en modèle mixte. Pourquoi est-ce le comportement attendu ?

### 3.3 Interpréter

7. Observer les effets aléatoires par nichoir (BLUPs)
8. Identifier les nichoirs qui s'écartent le plus de la moyenne générale

**Question 3.3 :** Un nichoir a un effet aléatoire très positif. Quelles causes biologiques pourraient expliquer que les poussins de ce nichoir soient systématiquement plus grands ?

### 3.4 Quand est-ce nécessaire ?

**Question 3.4 :** Dans les situations suivantes, faut-il un modèle mixte ? Justifier.
- a) 50 observations indépendantes sur 50 sites différents
- b) 10 observations par oiseau bagué sur 5 individus
- c) 30 sites, 1 observation par site, mais 3 années différentes

---

## Partie 4 — Domaines vitaux MCP et KDE (45 min)

### Contexte
Un Busard des roseaux (*Circus aeruginosus*) mâle a été équipé d'un émetteur GPS. 120 positions ont été enregistrées pendant la saison de reproduction.

### 4.1 Module MCP

1. Aller dans **Domaine vital — MCP**
2. Importer ou simuler des positions GPS (ou utiliser les données synthétiques)
3. Calculer le MCP 100%
4. Observer la surface en ha

5. Calculer le MCP 95% (exclure 5% des points extrêmes)
6. Observer la réduction de surface

**Question 4.1 :** Le MCP 100% est de 1850 ha et le MCP 95% est de 620 ha. Que révèle cette différence sur la distribution spatiale des positions ?

### 4.2 Module KDE

7. Aller dans **Domaine vital — KDE**
8. Utiliser les mêmes données
9. Observer l'isoplèthe 50% (zone noyau) et 95% (domaine complet)
10. Faire varier la bande passante h

**Question 4.2 :** Qu'observe-t-on sur la forme du domaine vital quand h est très grand (fort lissage) ? Et quand h est très petit ?

11. Comparer la surface KDE 95% avec le MCP 95%

**Question 4.3 :** Laquelle des deux méthodes (MCP ou KDE) est préférable pour identifier les zones de nidification et d'alimentation ? Justifier.

### 4.3 Application pratique

**Question 4.4 :** Le domaine vital KDE 50% du Busard chevauche une zone agricole intensive. Quelle information complémentaire faudrait-il avoir pour recommander une mesure de protection ?

---

## Questions de synthèse — Séance 2

**Question S2.1 :** Compléter le tableau de choix de méthode :

| Données | Variable réponse | Méthode recommandée |
|---------|-----------------|-------------------|
| 2 groupes, n = 20, distribution normale | Continue | ? |
| 3 groupes, n = 8, asymétrique | Continue | ? |
| Comptages sur 50 placettes, forte agrégation | Entière ≥ 0 | ? |
| 5 mesures par nichoir, 12 nichoirs | Continue, hiérarchique | ? |
| Positions GPS d'un individu | Coordonnées | ? |

**Question S2.2 :** Un collègue a fait un t-test sur des données groupées (plusieurs observations par site). Pourquoi son résultat risque-t-il d'être invalide ? Que lui recommandez-vous ?

**Question S2.3 :** Vous avez deux modèles pour les mêmes données : GLM Poisson (AIC = 342) et Binomial négatif (AIC = 318). Lequel choisissez-vous ? Et si les coefficients sont très similaires dans les deux modèles ?

---

## Pour aller plus loin

- Lire `docs/guide_scientifique.md` sections Tests statistiques, PVA
- Essayer les mêmes analyses sur un vrai jeu de données de comptages (STOC, Wetland Bird Survey)
- Explorer le Mode Enseignant pour voir les formules complètes des modèles GLM et mixtes
