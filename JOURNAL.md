# Journal de recherche

## J3 — Brute-force

**Méthode.** On essaie les suites de commandes des plus courtes aux plus
longues (parcours en largeur). On ignore les états déjà vus. La première suite
qui trie est donc la plus courte. Budget : 100 000 états au maximum.

**Mesures** (`go test -run ToutesPermutations -v`) :

| n | Permutations | Toutes résolues | K max | États gardés max | Durée totale |
|---|---|---|---|---|---|
| 1 | 1 | oui | 0 | 1 | < 1 ms |
| 2 | 2 | oui | 1 | 2 | < 1 ms |
| 3 | 6 | oui | 2 | 8 | < 1 ms |
| 4 | 24 | oui | 5 | 81 | 5 ms |
| 5 | 120 | oui | 8 | 689 | 261 ms |

Chaque suite trouvée a été rejouée par le vérificateur.

**Limite.** Le nombre de positions possibles vaut (n + 1) × n! : 720 pour
n = 5, mais 40 millions pour n = 10. Le temps passe de 5 ms à 261 ms entre
n = 4 et n = 5. On n'utilise donc le brute-force que jusqu'à n = 5.
Le budget n'a jamais été atteint (689 états au maximum).

**Ce qu'on en garde.** Les K minimaux servent de référence. Comme `Solve`
utilise cette recherche jusqu'à 5 nombres, il donne exactement le minimum sur
ces 153 permutations.

## J5 — Deux stratégies

1. **Sélection** : amener le minimum de A au sommet, `pb`, recommencer, puis
   tout remettre avec `pa`.
   *Correct* : B reçoit les nombres du plus petit au plus grand, donc les `pa`
   reconstruisent A triée.
   *Termine* : A perd un élément à chaque tour (variant : la taille de A).
2. **Radix** : remplacer les nombres par leur rang (0 à n−1), puis pour
   chaque chiffre binaire : `pb` si le chiffre vaut 0, `ra` sinon, puis tout
   remettre avec `pa`.
   *Termine* : chaque tour traite n éléments, et il y a au plus ⌈log₂ n⌉ tours.

## J6 — Itérations

### Itération 1 : choisir le sens de rotation

- **Hypothèse** : quand le minimum est dans la moitié basse de A, `rra` le
  fait monter plus vite que `ra`. On devrait diviser les rotations par 2
  environ.
- **Modification** : `SelectionV0` → `SelectionV1` (un `if` sur la position).
- **Mesure** (K médian, mêmes entrées) :

| Entrée | V0 | V1 | Gain |
|---|---|---|---|
| n=100 aléatoire | 2597 | 1466 | −44 % |
| n=500 aléatoire | 63170 | 32204 | −49 % |
| n=100 inversé | 5150 | 299 | −94 % |

- **Décision** : gardée. L'hypothèse est confirmée, et le gain est encore plus
  fort sur les entrées inversées (le minimum est toujours en bas : une seule
  `rra` suffit).

### Itération 2 : combiner les stratégies

- **Hypothèse** : aucune stratégie n'est la meilleure partout. Le radix
  gagne sur l'aléatoire, mais il ne profite pas d'une entrée presque triée.
- **Modification** : `Solve` calcule `SelectionV1` et `Radix` et garde la
  plus courte. Jusqu'à 5 nombres, il utilise le brute-force.
- **Mesure** (K médian) :

| Entrée | SelectionV1 | Radix | Solve |
|---|---|---|---|
| n=100 aléatoire | 1466 | 1084 | 1084 |
| n=100 presque trié | 210 | 1084 | 210 |
| n=500 aléatoire | 32204 | 6784 | 6784 |
| n=500 inversé | 1499 | 6784 | 1499 |

- **Coût** : environ 2 fois plus de temps (n=500 aléatoire : 19 ms au lieu
  de 7 ms pour le radix seul).
- **Décision** : gardée. Le meilleur K partout, pour un temps qui reste faible.

### Version abandonnée

`SelectionV0` n'est plus utilisée par le programme, mais elle reste dans le
code et dans les mesures comme point de départ.
