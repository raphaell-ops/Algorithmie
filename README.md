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
| `parser.go` | lecture et vérification des nombres |
| `stacks.go` | les deux piles et les 11 commandes |
| `checker.go` | le vérificateur |
| `brute.go` | la recherche brute-force |
| `solver.go` | les stratégies |
| `main.go` | le programme |
| `main_test.go` | tous les tests et les mesures |
| `CONTRAT.md` | entrée, commandes, sorties, statuts et cas limites |
| `ANALYSE.md` | analyse Big-O, mesures et choix final |
| `JOURNAL.md` | journal du brute-force et des itérations |

## Résumé

- Une pile est une slice, le sommet est à l'indice 0.
- `Solve` : brute-force jusqu'à 5 nombres (suite la plus courte), sinon la plus
  courte entre `SelectionV1` et `Radix`.
- K médian pour n = 500 : SelectionV0 63170, SelectionV1 32204, Radix 6784.
- Le minimum n'est garanti que jusqu'à 5 nombres.
