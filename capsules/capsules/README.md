# Capsules algo B1 : le projet piles

Ce dossier contient 7 capsules de cours pour le projet piles en Go.
Chaque capsule traite un thème avec des explications, des schémas et des exercices corrigés.

## Contenu du dossier

```
capsules/
├── README.md        ce fichier
├── build.py         script qui génère les capsules (vous n'en avez pas besoin)
└── site/
    ├── index.html   page d'accueil : commencez ici
    ├── 01-piles-et-instructions.html
    ├── 02-contrats-et-invariants.html
    ├── 03-tester.html
    ├── 04-le-verificateur.html
    ├── 05-representer-les-donnees.html
    ├── 06-mesurer-les-couts.html
    └── 07-copies-et-stabilite.html
```

## Ouvrir les capsules

1. Dézippez l'archive. Une capsule ouverte directement dans le zip ne s'affiche pas correctement.
2. Ouvrez `site/index.html` dans Chrome, Firefox ou Edge (double-clic).
3. Cliquez sur une capsule.

**Si l'affichage est cassé** (texte brut, pas de slides) : vérifiez votre connexion, puis essayez un autre navigateur.
Si ça ne marche toujours pas, lancez un petit serveur local depuis le dossier `site` :

```sh
cd site
python3 -m http.server 8000
```

Ouvrez ensuite <http://localhost:8000> dans le navigateur. `Ctrl+C` dans le terminal arrête le serveur.

## Naviguer

| Touche | Action |
|---|---|
| `→` ou `Espace` | avancer ; sur un exercice, afficher la solution |
| `←` | revenir en arrière |
| `Échap` | vue d'ensemble de toutes les slides |
| `F` | plein écran |

Sur téléphone ou tablette, balayez l'écran vers la gauche ou la droite.

## Ordre conseillé

Suivez les capsules dans l'ordre : chacune s'appuie sur les précédentes.

| # | Capsule | Ce que vous saurez faire |
|---|---|---|
| 01 | Les piles et les onze instructions | appliquer `sa`, `pb`, `rra`… à la main |
| 02 | Contrats et invariants | dire précisément ce qu'une instruction doit faire |
| 03 | Tester : cas normaux, cas limites | écrire des tests Go qui attrapent vraiment les bugs |
| 04 | Le vérificateur | juger une suite d'instructions : `OK`, `KO` ou `Error` |
| 05 | Représenter les données | choisir comment stocker une pile, comprendre le tampon circulaire |
| 06 | Mesurer les coûts | compter les écritures, lire un benchmark Go |
| 07 | Copies et stabilité des états | éviter les pièges des tranches Go partagées |

## Bien utiliser les exercices

Sur une slide d'exercice, la solution est cachée et apparaît quand vous appuyez sur `→`.

1. Lisez l'énoncé.
2. Cherchez sur papier ou dans un fichier Go **avant** d'appuyer sur `→`.
3. Comparez avec la solution. Si vous ne trouvez pas la même chose, cherchez où votre raisonnement a divergé.

La capsule 01 contient un **simulateur** : entrez des nombres, cliquez sur les instructions et regardez les piles bouger. Il sert à vérifier vos réponses aux exercices.

## Imprimer ou garder en PDF

Ajoutez `?print-pdf` à la fin de l'adresse d'une capsule, par exemple :

```
.../site/01-piles-et-instructions.html?print-pdf
```

Ensuite, faites Imprimer, puis Enregistrer en PDF. Mettez les marges à « Aucune » et cochez « Graphiques d'arrière-plan ».

## Besoin d'aide ?

Je reste disponible si vous bloquez sur une notion, un exercice ou votre code.

Pour que je puisse vous aider rapidement, envoyez-moi :

- la capsule et le numéro de slide concernés (il est affiché en haut à droite, par exemple `7 / 12`) ;
- ce que vous avez essayé et le résultat que vous obtenez ;
- pour un problème de code : le code concerné et le message d'erreur complet, copiés en texte plutôt qu'en capture d'écran.

