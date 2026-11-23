# Fiche de contrat

## Entrée

- Les nombres sont donnés en arguments : `go run . 3 2 1` ou `go run . "3 2" 1`.
- Chaque argument est découpé sur les espaces. Les nombres sont lus dans l'ordre.
- Un nombre s'écrit : un signe `+` ou `-` facultatif, puis au moins un chiffre.
- Les nombres doivent tenir dans un `int64`
  (de -9223372036854775808 à 9223372036854775807).
- Deux nombres égaux sont interdits, même écrits différemment (`1`, `+1`, `01`).
- Zéro argument est valide. Un argument vide ou blanc est une erreur.
- Le premier nombre est au sommet de A. B est vide au départ.

## Les commandes

Le sommet d'une pile est son premier élément. Chaque commande compte 1 dans le
score, même si elle ne change rien.

| Commande | Effet | Si impossible |
|---|---|---|
| `sa` / `sb` | échange les deux premiers éléments de A / B | rien ne change |
| `ss` | `sa` et `sb` | chaque partie agit si elle peut |
| `pa` | sommet de B → sommet de A | rien ne change si B est vide |
| `pb` | sommet de A → sommet de B | rien ne change si A est vide |
| `ra` / `rb` | sommet de A / B → fond | rien ne change si moins de 2 éléments |
| `rr` | `ra` et `rb` | chaque partie agit si elle peut |
| `rra` / `rrb` | fond de A / B → sommet | rien ne change si moins de 2 éléments |
| `rrr` | `rra` et `rrb` | chaque partie agit si elle peut |

Une commande inconnue est refusée : rien ne change et le score n'augmente pas.

## Arrivée

La suite est correcte si, à la fin :
1. toutes les commandes existent ;
2. B est vide ;
3. A est strictement croissante du sommet vers le fond ;
4. A contient exactement les nombres de départ.

C'est ce que vérifie `Verify` dans `checker.go`, en repartant d'une copie de
l'entrée originale.

## Sorties et statuts

| Cas | Sortie standard | Sortie d'erreur | Statut |
|---|---|---|---|
| Succès | une commande par ligne (rien si déjà trié) | rien | 0 |
| Entrée invalide | rien | `Error` | 1 |
| Erreur d'écriture | peut être incomplète | message | 3 |

Toute l'entrée est vérifiée avant d'afficher quoi que ce soit : une entrée
invalide ne produit jamais de commande.

Le statut 2 (limite de recherche) n'apparaît pas : si le brute-force atteint
son budget, `Solve` utilise les stratégies générales, qui terminent toujours.

## Cas préparés avant le code

| Type | Exemples |
|---|---|
| Acceptés | `3 1 2`, `"3 1" 2`, `+5 -3 007`, les bornes de `int64` |
| Refusés | `12a`, `-`, `1.5`, `""`, `"   "`, `9223372036854775808`, `1 +1`, `0 -0` |
| Limites | aucun argument, un seul nombre, déjà trié |

Tous ces cas sont dans `main_test.go`.
