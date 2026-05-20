# ORNI-LAB — Structure de présentation (45 min)

> Ce document est un plan de diaporama prêt à adapter dans PowerPoint, Google Slides, Beamer ou Canva.
> Chaque diapositive est décrite avec son contenu et les points à dire à l'oral.

---

## Diapositive 1 — Titre

**Titre :** ORNI-LAB — Laboratoire pédagogique interactif en écologie quantitative des oiseaux

**Sous-titre :** Formation à l'outil | [Date] | [Établissement]

**Visuel :** Logo ORNI-LAB, photo d'oiseau en fond

---

## Diapositive 2 — Pourquoi cet outil ?

**Titre :** Le problème pédagogique

**Contenu :**
- Les méthodes quantitatives en ornithologie sont abstraites à enseigner
- R et Python demandent une courbe d'apprentissage importante
- Les étudiants ont du mal à voir l'effet d'un paramètre sans coder

**Message clé :** ORNI-LAB permet d'explorer les modèles **sans programmer**, de façon interactive, en temps réel.

---

## Diapositive 3 — Vue d'ensemble

**Titre :** 18 simulateurs interactifs

**Contenu (deux colonnes) :**

| Biostatistique (8) | Dynamique des populations (10) |
|--------------------|-------------------------------|
| Analyse CSV | Richesse & diversité |
| Statistiques descriptives | Croissance exponentielle/logistique |
| Corrélation & régression | Matrices de Leslie |
| Tests statistiques | Capture-Marquage-Recapture |
| GLM comptage | Modèles d'occupation |
| Modèles mixtes | Distance sampling |
| Domaine vital — MCP | Lotka-Volterra |
| Domaine vital — KDE | Séries temporelles |
| | PVA & conservation |
| | Scénarios de gestion |

---

## Diapositive 4 — Les deux modes

**Titre :** S'adapter à chaque public

**Contenu :**

```
MODE ÉTUDIANT              MODE ENSEIGNANT
─────────────              ───────────────
• Interface épurée         • Tout le mode étudiant
• Graphiques interactifs   • Formules mathématiques
• Métriques clés           • Notes pédagogiques
• Interprétation guidée    • Hypothèses implicites
                           • Limites du modèle
```

**À l'oral :** "Le mode Enseignant s'active d'un clic dans la barre latérale. Il ajoute les formules LaTeX et les limites de chaque modèle — utile pour animer une discussion."

---

## Diapositive 5 — Démo live : interface

**Titre :** Prise en main en 2 minutes

**Contenu :**
1. Lancer ORNI-LAB.bat
2. Observer la barre latérale : mode → section → module
3. Choisir "Croissance exponentielle/logistique"
4. Bouger le curseur `r` (taux de croissance)
5. Observer le changement en temps réel sur le graphique

**À l'oral :** Faire la démo en direct. Montrer le hover sur le graphique Plotly.

---

## Diapositive 6 — Importer ses données

**Titre :** Travailler avec ses propres données

**Contenu :**
- Format CSV (séparateur auto-détecté : virgule, point-virgule, tabulation)
- Colonnes numériques et catégoriques identifiées automatiquement
- Valeurs manquantes détectées et signalées
- Compatible avec les exports de tableurs, loggers GPS, applications de terrain

**Visuel suggéré :** Screenshot du module Analyse CSV avec un fichier chargé

---

## Diapositive 7 — Module phare : PVA

**Titre :** Exemple — Analyse de viabilité des populations (PVA)

**Contenu :**
- Simule ~250 trajectoires stochastiques
- Paramètres : effectif initial N₀, taux de croissance r, variance σ², capacité de charge K, seuil de quasi-extinction
- Résultat : probabilité de quasi-extinction sur un horizon choisi
- Export PDF avec les paramètres et le résultat

**À l'oral :** "Un risque de quasi-extinction à 40% ne prédit pas une date d'extinction. Il mesure la fragilité de la population sous les hypothèses choisies."

---

## Diapositive 8 — Module phare : Matrices de Leslie

**Titre :** Exemple — Quelle classe d'âge pilote la dynamique ?

**Contenu :**
- Entrée : fécondités et survies par classe d'âge
- Calcul du taux de croissance asymptotique λ
- Analyse de sensibilité et d'élasticité : quel paramètre a le plus d'impact ?
- λ > 1 → croissance | λ = 1 → stabilité | λ < 1 → déclin

**À l'oral :** "L'élasticité permet de répondre à : si on améliore la survie des adultes de 10%, quel est l'effet sur λ ? C'est une question centrale en conservation."

---

## Diapositive 9 — Scénarios de gestion

**Titre :** Comparer des actions de conservation

**Contenu :**
Trois scénarios comparés en parallèle :
- **Restauration d'habitat** : augmenter K
- **Réduction de mortalité** : diminuer les pertes annuelles
- **Translocation** : augmenter N₀

Résultat : risque de quasi-extinction pour chaque scénario, médiane de l'effectif final

**À l'oral :** "Ce module permet à des étudiants de jouer le rôle de gestionnaires d'espèce menacée et de justifier leurs choix avec des chiffres."

---

## Diapositive 10 — Intégration pédagogique

**Titre :** Comment intégrer ORNI-LAB dans vos cours ?

**Contenu :**
- **Cours magistral** : démo live, visualiser l'effet d'un paramètre
- **TP en salle informatique** : fiches guidées par module
- **Travail personnel** : exploration libre avec export PDF/CSV
- **Évaluation** : exporter les résultats d'un scénario, rédiger une note d'interprétation

**Cursus suggéré :**
- Séance 1 : Biostat de base (CSV, stats desc, régression)
- Séance 2 : Biostat avancées (tests, GLM, LMM, GPS)
- Séance 3 : Dynamique (diversité, croissance, Leslie, CMR)
- Séance 4 : Conservation (occupation, PVA, scénarios)

---

## Diapositive 11 — Exports

**Titre :** Produire un rendu

**Contenu :**

| Format | Contenu | Usage |
|--------|---------|-------|
| PDF | Paramètres + résultats + interprétation | Rapport, compte-rendu |
| CSV | Données simulées ou analysées | Traitement dans R/Excel |
| PNG | Graphique (bouton Plotly) | Présentation, rapport |

---

## Diapositive 12 — Points d'attention scientifiques

**Titre :** Ce que l'outil ne fait pas

**Contenu :**
- Les jeux de données par défaut sont **synthétiques** : apprendre la méthode, pas produire une conclusion
- Une courbe bien ajustée ≠ validation du mécanisme biologique
- Une p-value faible ≠ importance écologique
- Un risque PVA dépend **fortement** des hypothèses sur la variance et le seuil
- La détectabilité des oiseaux n'est pas intégrée dans tous les modules

---

## Diapositive 13 — Ressources

**Titre :** Pour aller plus loin

**Contenu :**
- `docs/guide_scientifique.md` : variables, hypothèses, interprétations détaillées
- `docs/formation/` : fiches pédagogiques, TP, ce guide
- Mode Enseignant : notes et références bibliographiques dans chaque module
- Code source : chaque module expose ses fonctions de calcul testables séparément

---

## Diapositive 14 — Questions / Démo

**Titre :** Questions et exploration libre

**Contenu :**
- Démo guidée ou exploration libre par les participants
- Suggestion : chacun choisit un module et exporte un PDF

---

## Notes pour l'animateur

- Prévoir ORNI-LAB installé et lancé **avant** le début de la séance
- Tester le fichier CSV exemple en amont
- En salle informatique : distribuer le `01_GUIDE_INSTALLATION.md` pour l'installation autonome
- La démo des diapositives 5 à 9 peut être remplacée par une exploration guidée si le public est interactif
