# ORNI-LAB

ORNI-LAB est une application Streamlit pour l'enseignement quantitatif en ornithologie. Elle rassemble des simulateurs interactifs pour explorer les dynamiques de populations, les relations morphologiques, les tests statistiques et les decisions de conservation.

Le projet vise un usage pedagogique de niveau Master : les modeles sont volontairement lisibles, manipulables et exportables, mais ils doivent etre interpretes comme des outils d'apprentissage, pas comme des modeles de gestion directement calibrables sans donnees de terrain.

## Modules Disponibles

| Module | Question scientifique | Variables centrales |
| --- | --- | --- |
| Statistiques descriptives | Comment resumer des comptages ou mesures morphologiques ? | moyenne, mediane, ecart-type, distribution, habitat |
| Analyse CSV | Comment analyser rapidement un fichier de terrain importe ? | colonnes numeriques, groupes, valeurs manquantes, correlation, test de Welch |
| Croissance exponentielle/logistique | Une population augmente-t-elle sans limite ou vers une capacite de charge ? | `N0`, `r`, `K`, horizon, effectif final |
| Matrices de Leslie | Quelle classe d'age pilote la croissance de la population ? | fecondites `F`, survies `S`, structure initiale, `lambda` |
| Correlation et regression | Deux variables biologiques varient-elles ensemble ? | pente, intercept, `r` de Pearson, `R2`, p-value |
| Capture-Marquage-Recapture | Quelle est l'abondance probable d'une population difficile a compter ? | marques `M`, captures `C`, recaptures `R`, IC 95 % |
| Lotka-Volterra | Comment proies et predateurs oscillent-ils ? | `alpha`, `beta`, `delta`, `gamma`, equilibre theorique |
| Tests statistiques | La difference entre deux groupes est-elle compatible avec le hasard ? | tailles d'echantillon, moyennes, variance, p-value |
| PVA et conservation | Quel risque de quasi-extinction sous incertitude ? | `N0`, `r`, `sd_r`, `K`, seuil, pertes, iterations |
| Scenarios de gestion | Quelle action reduit le plus le risque ? | croissance, variance, pertes, capacite de charge, risque |

Le guide detaille des variables et interpretations se trouve dans [docs/guide_scientifique.md](docs/guide_scientifique.md).

## Installation

Depuis PowerShell :

```powershell
cd "C:\Users\DELL Latitude 7480\Documents\GitHub\Outils_Ornitho"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Si les dependances existent deja sur la machine, l'environnement virtuel reste recommande pour eviter les conflits de versions.

## Lancement

```powershell
python -m streamlit run app.py
```

Puis ouvrir :

```text
http://localhost:8501
```

## Utilisation Pedagogique

1. Choisir le mode dans la barre laterale.
2. Selectionner un simulateur.
3. Modifier une variable a la fois pour isoler son effet.
4. Lire les indicateurs numeriques avant d'interpreter le graphique.
5. Exporter les resultats en CSV ou PDF pour discussion, rapport ou exercice.

Le mode etudiant privilegie l'intuition et les interpretations guidees. Le mode enseignant ajoute des notes de discussion, les hypotheses implicites et les limites mathematiques.

## Architecture

```text
.
|-- app.py
|-- app/
|   |-- main.py
|   `-- config.py
|-- modules/
|   |-- descriptive_stats.py
|   |-- csv_analysis.py
|   |-- growth.py
|   |-- leslie.py
|   |-- regression.py
|   |-- cmr.py
|   |-- lotka_volterra.py
|   |-- statistical_tests.py
|   |-- pva_conservation.py
|   `-- management_scenarios.py
|-- simulations/
|   `-- pva_engine.py
|-- core/
|   `-- export.py
|-- data/
|   `-- examples.py
|-- utils/
|   `-- ui.py
|-- models/
|   `-- ai_tutor.py
|-- docs/
|   `-- guide_scientifique.md
`-- tests/
    `-- test_models.py
```

Chaque fichier dans `modules/` expose une fonction `render(context)`. Les calculs reutilisables sont separes quand ils ont une valeur testable, par exemple `simulate_growth`, `build_leslie_matrix`, `lincoln_petersen` et `simulate_pva`.

## Tests

```powershell
python -m unittest discover -s tests
```

Les tests couvrent les fonctions numeriques critiques, les cas limites des modeles de croissance et de PVA, et la generation PDF.

## Points D'attention Scientifiques

- Les jeux de donnees fournis sont synthetiques. Ils servent a apprendre une methode, pas a produire une conclusion biologique reelle.
- Les modeles supposent souvent des parametres constants, des observations independantes ou une population fermee.
- Une p-value faible ne suffit pas a prouver une importance ecologique.
- Un risque PVA depend fortement des hypotheses sur la variance, les pertes annuelles et le seuil de quasi-extinction.
- Une courbe bien ajustee ne valide pas automatiquement le mecanisme biologique sous-jacent.

## Exports

Les modules peuvent exporter :

- les donnees simulees en CSV ;
- un resume PDF compact via `reportlab`.

Les symboles scientifiques les plus courants sont normalises dans les PDF pour eviter les problemes de rendu avec les polices standards.
