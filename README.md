# Attribution Marketing par Chaîne de Markov

Ce projet implémente un pipeline complet d’analyse d’attribution marketing basé sur une **chaîne de Markov absorbante**. L’objectif est de déterminer l’influence de différents points de contact (expositions TV, programmatique, etc.) sur la probabilité de conversion (achat), en calculant notamment les **effets de suppression** de chaque canal pour attribuer le nombre de conversions à chaque point de contact.

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Arborescence du projet](#arborescence-du-projet)
3. [Installation](#installation)
4. [Description des modules](#description-des-modules)
5. [Préparation des données](#préparation-des-données)
6. [Exécution du pipeline](#exécution-du-pipeline)
7. [Résultats générés](#résultats-générés)
8. [Personnalisation / Extensions](#personnalisation--extensions)
9. [FAQ & Dépannage](#faq--dépannage)

---

## 1. Prérequis

* **Système d’exploitation** : macOS (ou Linux) — le tri du CSV utilise la commande `sort` native.
* **Python 3.8+**
* **Environnement virtuel Python** (`venv`)
* **Accès en lecture** aux fichiers CSV d’entrée (Retailer, TV, Programmatique, Mapping, Sociodémographie).
* **Espace disque** suffisant pour stocker les fichiers intermédiaires (CSV consolidés, triés, matrices) et les résultats.

---

## 2. Arborescence du projet

```plaintext
marketing_attribution_markov/
├── .venv/                          # Environnement virtuel Python
├── data/                           # Dossier des données brutes CSV
│   ├── retailer.csv                # Transactions/Achats (Retailer)
│   ├── exposures_tv.csv            # Expositions TV
│   ├── exposures_programmatique.csv# Expositions Programmatique
│   ├── id_mapping.csv              # Mapping device_id / dsp_id → customer_id
│   └── demographics.csv            # Données socio-démographiques (optionnel)
├── data/processed/                 # Dossier pour les fichiers intermédiaires
│   ├── merged_data.csv             # Fichier consolidé non trié (généré automatiquement)
│   └── merged_sorted.csv           # Fichier consolidé trié (généré automatiquement)
├── results/                        # Dossier de sortie des résultats
│   ├── matrices/                   # Matrices (transition, attribution)
│   ├── figures/                    # Graphiques générés (heatmaps, bar charts)
│   └── logs/                       # Fichier de logs du pipeline (`pipeline.log`)
├── src/                            # Code source Python
│   ├── __init__.py
│   ├── config.py                   # Configuration des chemins et paramètres
│   ├── data_loading.py             # Chargement (pandas) des CSV minimal (mapping, Retailer)
│   ├── preprocessing.py            # Prétraitement “en streaming” (lecture CSV pure)
│   ├── transition_counter.py       # Comptage des transitions ligne à ligne
│   ├── markov_model.py             # Calcul de la matrice de transition & taux de conversion
│   ├── attribution.py              # Effets de suppression et calcul des conversions attribuées
│   └── visualization.py            # Fonctions de génération des graphiques (matplotlib/seaborn)
├── main.py                         # Script principal pour lancer le pipeline complet
├── requirements.txt                # Liste des dépendances Python
└── README.md                       # Documentation du projet (ce fichier)
```

---

## 3. Installation

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/votre-compte/marketing_attribution_markov.git
   cd marketing_attribution_markov
   ```

2. **Création et activation d’un environnement virtuel**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   # Sous Windows : .venv\Scripts\activate
   ```

3. **Installation des dépendances**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   Le fichier `requirements.txt` contient au minimum :

   ```
   pandas>=1.2
   numpy>=1.19
   matplotlib>=3.3
   seaborn>=0.11
   ```

4. **Création des dossiers de sortie**

   Assurez-vous que les dossiers suivants existent (sinon, créez‐les) :

   ```bash
   mkdir -p data/processed
   mkdir -p results/matrices
   mkdir -p results/figures
   mkdir -p results/logs
   ```

   * `data/processed/` servira à recevoir les fichiers CSV générés par le prétraitement.
   * `results/matrices/` contiendra la matrice de transition et le tableau d’attribution final.
   * `results/figures/` contiendra les heatmaps et graphiques d’attribution.
   * `results/logs/` contiendra le fichier `pipeline.log` avec les traces d’exécution.

---

## 4. Description des modules

### 4.1 `src/config.py`

* Définit les chemins absolus vers les fichiers de données et de résultats (à base de `pathlib.Path`).
* Paramètres globaux (par ex. `MARKOV_ORDER` pour indiquer l’ordre de la chaîne de Markov, ici toujours 1).

**Exemples de variables exposées** :

```python
ROOT_DIR         # Répertoire racine du projet
DATA_DIR         # Répertoire “data/”
CSV_RETAILER     # data/retailer.csv
CSV_EXPOS_TV     # data/exposures_tv.csv
CSV_EXPOS_PRG    # data/exposures_programmatique.csv
CSV_ID_MAPPING   # data/id_mapping.csv
CSV_DEMOGRAPHICS # data/demographics.csv
RESULTS_DIR      # Répertoire “results/”
MATRICES_DIR     # results/matrices/
FIGURES_DIR      # results/figures/
LOGS_DIR         # results/logs/
```

---

### 4.2 `src/data_loading.py`

* Charge, au besoin, les fichiers CSV “petits” directement en DataFrame pandas.
* Sert à recharger le fichier `retailer.csv` pour compter le nombre total de clients convertis.

Fonctions principales :

* `load_retailer_events()` → DataFrame de `data/retailer.csv`.
* `load_id_mapping()` → DataFrame de `data/id_mapping.csv`.
* `load_demographics()` → DataFrame de `data/demographics.csv` (optionnel).

Note : Le prétraitement “lourd” (TV, Programmatique, Retailer) s’effectue désormais sans pandas dans `preprocessing.py` pour économiser la RAM.

---

### 4.3 `src/preprocessing.py`

* **Lecture “pure CSV”** (module `csv` de la stdlib) pour minimiser l’empreinte mémoire.

* Charge d’abord `id_mapping.csv` en deux dictionnaires (mapping `device_id`→`customer_id`, `dsp_id`→`customer_id`), qui tiennent en RAM car relativement petits.

* Parcourt ensuite ligne par ligne :

  1. **`data/exposures_tv.csv`** : si `device_id` est mappé, écrit (`customer_id`, `timestamp_utc`, `TV`, `TV`) dans `data/processed/merged_data.csv`.
  2. **`data/exposures_programmatique.csv`** : si `dsp_id` est mappé, construit `state = "Prog_<campaign_name>"`, `channel = "Programmatique"`, écrit (`customer_id`, `timestamp_utc`, `state`, `channel`) dans le même `merged_data.csv`.
  3. **`data/retailer.csv`** : écrit chaque ligne comme (`customer_id`, `timestamp_utc`, `Conversion`, `Retailer`) dans `merged_data.csv`.

* **Sortie** :

  * `data/processed/merged_data.csv` (colonnes : `customer_id,timestamp,state,channel`) — non trié.
  * N’accumule jamais plus qu’une ligne de CSV et les deux dictionnaires de mapping en mémoire.

**Fonction exposée** :

```python
def preprocess_data_in_chunks():
    """
    Retourne le chemin du fichier consolidé non trié (merged_data.csv).
    """
```

---

### 4.4 `src/transition_counter.py`

* Parcourt en **streaming** le fichier *trié* `data/processed/merged_sorted.csv`.

* Pour chaque ligne (chaque interaction d’un client), il reconstruit “à la volée” le dernier état du client pour comptabiliser les transitions.

  * Si le `customer_id` change, on clôture l’ancien parcours par une transition `(dernier état, No_Conversion)` s’il n’était pas déjà “Conversion”.
  * Pour chaque nouvel événement : incrémente `transition_counts[(état_précédent, état_courant)]`.
  * Si l’événement est `Conversion` : ajoute aussi `(Conversion, Conversion)` pour faire de “Conversion” un état absorbant, puis redémarre le parcours au même client avec `prev_state = 'Start'`.

* **Sortie** :

  * `transition_counts` : dictionnaire `dict[(src_state, dst_state) → count]`
  * `states_set` : ensemble de tous les états observés, incluant `{'Start', 'Conversion', 'No_Conversion', 'TV', 'Prog_<...>'}`

* **Fonction exposée** :

```python
def compute_transition_counts_from_file(sorted_csv_path):
    """
    Lit merged_sorted.csv trié (customer_id, timestamp) et renvoie (transition_counts, states_set).
    """
```

* **Fonction utilitaire** :

```python
def build_transition_matrix(transition_counts, states_set):
    """
    Construit un DataFrame pandas de la matrice de transition (proba) à partir des counts.
    """
```

---

### 4.5 `src/markov_model.py`

* À partir de la **matrice de transition** (DataFrame, taille N×N), extrait :

  * Les états non absorbants (c.-à-d. ceux ≠ `Conversion` et ≠ `No_Conversion`).
  * Les sous‐matrices `Q` (non absorbants → non absorbants) et `R` (non absorbants → absorbants).

* Calcule la **matrice fondamentale** $N = (I - Q)^{-1}$ et la matrice d’absorption $B = N \times R$.

* Extrait la **probabilité d’absorption dans “Conversion” à partir de “Start”**.

* **Fonction exposée** :

```python
def compute_conversion_rate(transition_matrix):
    """
    Retourne la probabilité que, parti de 'Start', on finisse absorbé en 'Conversion'.
    """
```

---

### 4.6 `src/attribution.py`

* **Effet de suppression** (*Removal Effect*) :
  Pour chaque canal (état non absorbant, ≠ `Start`, `Conversion`, `No_Conversion`), on :

  1. Supprime la ligne et la colonne correspondantes dans la matrice de transition (état retiré).
  2. Recalcule `new_conv_rate = compute_conversion_rate(matrice_sans_ce_canal)`.
  3. L’**effet** = `base_conv_rate - new_conv_rate`.

* **Attribution finale** :

  * Calcule la somme des effets de suppression (S).
  * Pour chaque état :

    ```
    proportion_canal = effet_canal / S  
    conversions_attribuées = proportion_canal * total_conversions_réelles
    ```

    où `total_conversions_réelles` = nombre unique de `customer_id` ayant au moins une conversion dans `retailer.csv`.

* **Fonctions exposées** :

```python
def compute_all_removal_effects(transition_matrix, base_conv_rate):
    """
    Retourne un dict {etat: effet_de_suppression}.
    """

def compute_channel_attribution(removal_effects, total_conversions):
    """
    Retourne un DataFrame indexé par canal avec colonnes
    ['removal_effect', 'proportion', 'conversions_attribuees'].
    """
```

---

### 4.7 `src/visualization.py`

* Génère les graphiques de sortie (matrice de transition + attribution) au format PNG :

  * **Heatmap** de la matrice de transition (fonction `plot_transition_matrix(...)`).
  * **Bar chart** des conversions attribuées par canal (fonction `plot_channel_attribution(...)`).

* Ces fonctions utilisent `matplotlib` et `seaborn`.

* Les images sont enregistrées sous `results/figures/`.

---

## 5. Préparation des données

Ce pipeline s’appuie sur **cinq** fichiers CSV d’entrée placés dans `data/` :

1. **`retailer.csv`**

   * Colonnes attendues :

     ```
     customer_id, timestamp_utc, event_name, brand, product_name, sales, quantity
     ```
   * Correspond aux transactions ou achats d’un client chez le retailer.
   * Exigence minimum : `customer_id` + `timestamp_utc`.

2. **`exposures_tv.csv`**

   * Colonnes attendues :

     ```
     device_id, timestamp_utc, cost_milli_cent
     ```
   * Chaque ligne = une impression TV (par ex. “flux publicitaire s’affiche sur la box”).

3. **`exposures_programmatique.csv`**

   * Colonnes attendues :

     ```
     dsp_id, timestamp_utc, campaign_name, device_type, cost_milli_cent
     ```

4. **`id_mapping.csv`**

   * Colonnes attendues :

     ```
     customer_id, device_id, dsp_id
     ```
   * Permet de relier chaque `device_id` (TV) ou `dsp_id` (programmation) à l’`customer_id` du retailer.

5. **`demographics.csv`** (optionnel)

   * Colonnes attendues :

     ```
     customer_id, breed, age, income
     ```
   * Données sociodémographiques qu’on pourrait utiliser ultérieurement pour segmenter le modèle.
   * Dans la version courante, on ne l’utilise pas pour le pipeline Markov, mais on peut la charger pour enrichir les données.

---

## 6. Exécution du pipeline

Une fois l’environnement configuré (cf. Section 3) et les fichiers CSV placés dans `data/`, lancez :

```bash
(.venv) $ python main.py
```

Le pipeline se déroule en plusieurs étapes, tracées dans le log :

1. **Étape 1 : Prétraitement “en streaming”**

   * Appelle `preprocessing.preprocess_data_in_chunks()`.
   * Génère `data/processed/merged_data.csv` (non trié).

2. **Étape 2 : Tri du CSV consolidé**

   * Exécute la commande :

     ```bash
     sort -t, -k1,1 -k2,2 data/processed/merged_data.csv \
           -o data/processed/merged_sorted.csv
     ```
   * Produit `data/processed/merged_sorted.csv`, trié par `customer_id` puis `timestamp`.

3. **Étape 3 : Comptage des transitions**

   * Appelle `transition_counter.compute_transition_counts_from_file('merged_sorted.csv')`.
   * Génère un dictionnaire `transition_counts` et un `states_set`.

4. **Étape 4 : Construction de la matrice de transition**

   * Appelle `transition_counter.build_transition_matrix(...)`.
   * Enregistre la matrice dans `results/matrices/transition_matrix.csv`.

5. **Étape 5 : Calcul du taux de conversion global**

   * Appelle `markov_model.compute_conversion_rate(trans_matrix)`.
   * Affiche le taux estimé (`base_conv_rate`).

6. **Étape 6 : Effets de suppression & attribution**

   * Appelle `attribution.compute_all_removal_effects(trans_matrix, base_conv_rate)`.
   * Recharge `retailer.csv` via `data_loading.load_retailer_events()` pour déterminer `total_conversions` (nombre unique de `customer_id`).
   * Appelle `attribution.compute_channel_attribution(removal_effects, total_conversions)`.
   * Sauvegarde le résultat dans `results/matrices/attribution_by_channel.csv`.

7. **Étape 7 : Visualisations**

   * Génère et enregistre :

     * `results/figures/transition_matrix_heatmap.png`
     * `results/figures/attribution_bar_chart.png`

8. **Fin**

   * Tous les résultats sont disponibles dans le dossier `results/`.
   * Le fichier `results/logs/pipeline.log` contient le détail de l’exécution (horodatages, infos).

---

## 7. Résultats générés

Une fois le pipeline terminé, vous trouverez :

1. **`results/matrices/transition_matrix.csv`**

   * CSV de la matrice de transition N×N (N = nombre d’états).
   * En-têtes : noms des états (start, TV, Prog\_<...>, Conversion, No\_Conversion).

2. **`results/matrices/attribution_by_channel.csv`**

   * CSV listant, pour chaque canal (état intermédiaire) :

     ```
     removal_effect, proportion, conversions_attribuees
     ```
   * `removal_effect` = baisse du taux de conversion si on retire le canal.
   * `proportion` = part relative de cet effet parmi tous les canaux.
   * `conversions_attribuees` = nombre de conversions allouées à ce canal (en pondérant par le total réel).

3. **`results/figures/transition_matrix_heatmap.png`**

   * Heatmap visuelle de la matrice de transition (valeurs entre 0 et 1).
   * Permet de voir quelles transitions sont les plus fréquentes (couleurs plus claires).

4. **`results/figures/attribution_bar_chart.png`**

   * Diagramme en barres du nombre de conversions attribuées par canal.
   * Utile pour présenter rapidement la répartition des conversions par point de contact marketing.

5. **`results/logs/pipeline.log`**

   * Trace complète (INFO) des étapes :

     * Horodatages de début/fin de chaque étape.
     * Nombre de lignes lues, nombre d’états identifiés, taux de conversion calculé, etc.
   * Permet de diagnostiquer ou d’auditer le pipeline.

---

## 8. Personnalisation / Extensions

1. **Filtrage temporel**

   * Si vous souhaitez analyser une plage de dates spécifique, éditez `src/preprocessing.py` pour ne prendre que les lignes dont `timestamp` est dans l’intervalle souhaité (ex. entre `2025-01-01` et `2025-03-31`).
   * Vous pouvez aussi supprimer les “Conversions” dont la date est antérieure à toute exposition (pour éviter un biais “Start→Conversion”).

2. **Segmentation par profil**

   * Chargez `demographics.csv` (client → âge, income, etc.).
   * Créez des sous‐ensembles de `merged_sorted.csv` (ex. uniquement les 18-25 ans) et exécutez le pipeline séparément pour chaque segment.
   * Cela vous donnera une matrice de transition et un calcul d’attribution par segment de population.

3. **Ordre supérieur de la chaîne de Markov**

   * Actuellement, on suppose un modèle *Premier-ordre* (l’état suivant dépend uniquement de l’état courant).
   * Si vous souhaitez intégrer l’historique des deux derniers états (Markov d’ordre 2), il faudrait :

     * Redéfinir la notion “d’état” comme paire `(état_t−1, état_t)` et ajuster le comptage des transitions en conséquence.
     * Adapter `transition_counter` pour générer ces paires, et `markov_model` pour construire la nouvelle matrice.
   * Attention : le nombre d’états croît rapidement (combinaisons de deux états), donc le calcul peut devenir lourd.

4. **Visualisations avancées**

   * Ajoutez un graphique temporel de l’évolution des probabilités de conversion par canal, en découpant par fenêtre glissante (par exemple, chaque trimestre).
   * Générez un graphique “Sankey” représentant les flux de transition les plus fréquents.

5. **Tests unitaires**

   * Créez, si nécessaire, des tests sous `tests/` (avec `pytest`) pour assurer que chaque module fonctionne correctement (ex. que `compute_transition_matrix` renvoie une matrice dont chaque ligne somme à 1).

---

## 9. FAQ & Dépannage

### Q1 : Le script est “Killed” même après la version “pure CSV”

* **Cause probable** : manque de mémoire vive lors de la phase de tri (`sort`) si le fichier est gigantesque.
* **Solution** :

  * Exécutez la commande `sort` manuellement en découpant le CSV en plus petits morceaux.
  * Par exemple :

    ```bash
    split -l 500000 data/processed/merged_data.csv part_  # découpe en fichiers de 500 000 lignes
    sort -t, -k1,1 -k2,2 part_aa -o part_aa_sorted.csv
    sort -t, -k1,1 -k2,2 part_ab -o part_ab_sorted.csv
    # ... répétez pour chaque part_*
    # Puis concaténez et re‐tri globalement (approche “tri par fusion”)
    cat part_*_sorted.csv > merged_sorted_pre.csv
    sort -t, -k1,1 -k2,2 merged_sorted_pre.csv -o data/processed/merged_sorted.csv
    ```
  * Sur macOS, la commande `sort` peut manquer de RAM si le fichier ne tient pas dans `/tmp`. Utilisez l’option `-T` pour spécifier un dossier temporaire sur un disque plus grand :

    ```bash
    sort -T /Volumes/DisqueExterne/tmp -t, -k1,1 -k2,2 merged_data.csv -o merged_sorted.csv
    ```

### Q2 : Les valeurs “Start→Conversion” sont trop élevées

* **Vérifier le mapping** :

  * Assurez-vous que `id_mapping.csv` couvre la majorité des devices/dsp.
  * Sinon, de nombreux clients achètent sans qu’on ait jamais enregistré d’exposition, d’où le “Start→Conversion” massif.
* **Option de filtrage** :

  * Ne conservez dans `merged_data.csv` que les “Conversion” pour lesquels existe au moins une ligne d’exposition antérieure pour le même `customer_id`.
  * Cette règle peut être mise avant la phase de tri, en stockant dans un set tous les `customer_id` présents dans TV/Programmation, puis en n’écrivant dans “Conversion” que si le client apparaît dans ce set.

### Q3 : “KeyError” ou “ValueError” pendant la construction de la matrice

* **Erreurs possibles** :

  * Si un état intermédiaire apparaît dans `transition_counts` mais pas dans `states_set` (improbable si on ajoute toujours chaque état dans `states_set`).
  * Si `transition_matrix` ne contient pas “Start” ou “Conversion” ou “No\_Conversion”.
* **Solutions** :

  * Vérifiez que `merged_sorted.csv` contient bien au moins une ligne avec `state='Conversion'`.
  * Vérifiez, avant l’appel à `compute_conversion_rate`, que :

    ```python
    assert 'Start' in trans_matrix.index
    assert 'Conversion' in trans_matrix.index
    assert 'No_Conversion' in trans_matrix.index
    ```
  * Si un de ces états manque, inspectez `merged_sorted.csv` pour comprendre pourquoi (p. ex. pas d’état “No\_Conversion” car chaque client s’est converti, ou pas d’état “Conversion” du tout).

### Q4 : Les graphiques ne s’enregistrent pas

* Vérifiez que le dossier `results/figures` existe et a les droits d’écriture.
* Contrôlez que la variable `FIGURES_DIR` pointe bien vers `results/figures`.
* Si `seaborn` ou `matplotlib` posent problème, essayez de tracer en interactive (`plt.show()`) pour diagnostiquer.

### Q5 : Comment ajouter un nouveau canal (par ex. “Email”) ?

1. Dans le prétraitement (« streaming »), détectez les lignes correspondantes à “Email” (selon un nouveau CSV ou si “exposures\_programmatique.csv” contient un “campaign\_name=Email”).
2. Ajoutez `state='Email'` et `channel='Email'` pour ces lignes.
3. Relancez le pipeline : le nouvel état “Email” apparaîtra dans `states_set` et la matrice de transition intégrera automatiquement ses transitions.

---

> **Note finale**
> Ce pipeline est conçu pour être **léger en mémoire** et **émérite** (il produit un état de la chaîne de Markov complet à chaque exécution). Pour des volumes de données extrêmement importants, la clé est d’ajuster la méthode de tri (`sort`) ou de passer à une solution distribuée (Hadoop/Spark) pour le prétraitement. Cependant, pour la plupart des cas de taille “moyenne” (quelques dizaines de millions de lignes), cette approche en pur streaming et tri Unix s’avère robuste et reproductible.

Bonne exploitation des résultats d’attribution !

Made by ❤️ for Zohra