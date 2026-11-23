# Push-Swap en Go

## Lancer

```
go run . 3 2 1                      # affiche les commandes qui trient
go test                             # lance les tests
go test -v                          # avec le détail et les mesures
go test -run Comparaison -v         # comparaison des stratégies
go test -run ToutesPermutations -v  # mesures du brute-force
```

## Fichiers

| Fichier | Contenu |
|---|---|
| `parser.go` | J1 : lecture et vérification des nombres |
| `stacks.go` | J2 : les deux piles et les 11 commandes |
| `checker.go` | J2 : le vérificateur |
| `brute.go` | J3 : la recherche brute-force |
| `solver.go` | J5/J6 : les stratégies |
| `main.go` | le programme |
| `main_test.go` | tous les tests et les mesures |
| `CONTRAT.md` | fiche de contrat |
| `ANALYSE.md` | analyse Big-O, mesures et choix final |
| `JOURNAL.md` | journal du brute-force et des itérations |

## Sorties

| Cas | Sortie standard | Sortie d'erreur | Statut |
|---|---|---|---|
| Succès | une commande par ligne | rien | 0 |
| Entrée invalide | rien | `Error` | 1 |
| Erreur d'écriture | peut être incomplète | message | 3 |

## Choix et coûts

- Une pile est une slice, le sommet est à l'indice 0.
- `sa`, `sb`, `ss` : O(1). `ra`, `rra`, `pa`, `pb` : O(n), car il faut
  décaler tous les éléments. Chaque commande compte quand même 1 dans le score.
- `NewStacks` et `Clone` copient les piles : sinon deux variables
  partageraient les mêmes données et un état gardé de côté changerait.

## Brute-force

On essaie les suites les plus courtes d'abord. La première suite trouvée est
donc la plus courte. On ne garde pas deux fois le même état. Toutes les
permutations jusqu'à 5 nombres sont résolues (au pire 8 commandes pour n = 5).
Au-delà, il y a trop d'états : on ne l'utilise que pour n ≤ 5.

## Stratégies (K médian sur 20 mélanges aléatoires)

| Stratégie | n = 100 | n = 500 |
|---|---|---|
| SelectionV0 : le minimum monte avec `ra` puis `pb` | 2597 | 63170 |
| SelectionV1 : `ra` ou `rra` selon le plus court | 1466 | 32204 |
| Radix : tri sur les chiffres binaires des rangs | 1084 | 6784 |

Les résultats complets (entrées triées, inversées, presque triées) sont dans `ANALYSE.md`.

- Itération 1 (V0 → V1) : environ deux fois moins de commandes.
- Itération 2 (`Solve`) : brute-force jusqu'à 5 nombres (suite la plus courte),
  sinon la plus courte entre SelectionV1 et Radix.

## Limites

La suite la plus courte n'est garantie que jusqu'à 5 nombres. Au-delà,
les résultats sont des mesures, pas des garanties.
