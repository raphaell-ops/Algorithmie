# Analyse des coûts

**Modèle.** n est le nombre de valeurs. On compte :
- **K**, le nombre de commandes affichées (le score) ;
- **T**, le travail réel du programme (les cases lues ou écrites) ;
- **M**, la mémoire utilisée en plus de l'entrée.

## 1. Représentation choisie

Chaque pile est une slice, avec le sommet à l'indice 0. C'est la même
convention que le sujet, donc le code se lit comme l'énoncé.

## 2. Coût de chaque commande (T)

| Commande | T | Pourquoi |
|---|---|---|
| `sa`, `sb`, `ss` | O(1) | on échange 2 cases |
| `ra`, `rb`, `rra`, `rrb`, `rr`, `rrr` | O(n) | la boucle décale toutes les cases |
| `pa`, `pb` | O(n) | `append` crée une nouvelle slice et recopie la pile |

Chaque commande vaut 1 dans K, mais pas forcément 1 dans T.

## 3. Copies et mémoire

| Endroit | Copie | Pourquoi elle est nécessaire |
|---|---|---|
| `NewStacks` | n valeurs, une fois | ne pas modifier l'entrée originale |
| `Clone` | n valeurs à chaque appel | garder un état qui ne bouge plus (brute-force) |
| `push` | une nouvelle slice à chaque `pa`/`pb` | conséquence du sommet à l'indice 0 |

Sans copie, deux slices partagent les mêmes cases : modifier l'une modifie
l'autre (testé dans `TestEntreeConservee` et `TestCloneStable`).

## 4. Coût des algorithmes

| Algorithme | K | T | M |
|---|---|---|---|
| `SelectionV0` | O(n²), pire cas n(n−1)/2 + 2n | O(n³) | O(n + K) |
| `SelectionV1` | O(n²), environ n²/4 + 2n au pire | O(n³) | O(n + K) |
| `Radix` | O(n log n), au plus 2n × ⌈log₂ n⌉ | O(n² log n) | O(n + K) |
| `BruteForce` | minimal | O(11 × S² × n) | O(S × (n + K)) |
| `Solve` (n > 5) | min(SelectionV1, Radix) | T(SelectionV1) + T(Radix) | O(n + K) |

S est le nombre d'états gardés par le brute-force. Pour savoir si un état a
déjà été vu, on parcourt la liste des états gardés (S comparaisons), d'où le S².
Avec n ≤ 5, S reste inférieur à 700.

**Explications :**
- **Sélection** : pour chacun des n éléments, on fait jusqu'à n rotations,
  donc K = O(n²). Chaque rotation coûte O(n), donc T = O(n³).
- **Radix** : il y a ⌈log₂ n⌉ chiffres binaires. Pour chacun, on fait n
  commandes puis au plus n `pa`, donc K = O(n log n). Le calcul des rangs
  compare chaque valeur à toutes les autres : O(n²).
- **M** : on garde les deux piles (n valeurs) et la liste des commandes (K).

## 5. Mesures

Machine : Linux, Go 1.22.2, processeur Intel Xeon 2,8 GHz. Les K sont
identiques sur toutes les machines ; les durées changent.

Pour refaire les mesures : `go test -run Comparaison -v`

**K médian** (20 mélanges aléatoires, 1 entrée triée, 1 inversée, 5 presque triées) :

| n | Entrée | SelectionV0 | SelectionV1 | Radix | Solve |
|---|---|---|---|---|---|
| 100 | aléatoire | 2597 | 1466 | 1084 | 1084 |
| 100 | trié | 0 | 0 | 0 | 0 |
| 100 | inversé | 5150 | 299 | 1084 | 299 |
| 100 | presque trié | 447 | 210 | 1084 | 210 |
| 500 | aléatoire | 63170 | 32204 | 6784 | 6784 |
| 500 | trié | 0 | 0 | 0 | 0 |
| 500 | inversé | 125750 | 1499 | 6784 | 1499 |
| 500 | presque trié | 1962 | 1010 | 6784 | 1010 |

**Durée moyenne pour n = 500, aléatoire :**
SelectionV0 31 ms, SelectionV1 16 ms, Radix 7 ms, Solve 19 ms.

**Ce que montrent les mesures :**
- Les chiffres suivent l'analyse : de 100 à 500 (× 5), la sélection est
  multipliée par environ 22 (proche de 25 = 5²), le radix par environ 6
  (proche de n log n).
- Aucune stratégie n'est la meilleure partout : le radix gagne sur les entrées
  aléatoires, la sélection sur les entrées inversées ou presque triées.

## 6. Choix final

`Solve` utilise :
- le brute-force jusqu'à 5 nombres (suite la plus courte prouvée) ;
- sinon, la plus courte entre `SelectionV1` et `Radix`.

Ce choix donne le meilleur K sur toutes les familles mesurées. Le prix à payer
est un temps environ doublé, puisqu'on calcule les deux suites. Pour 500
nombres, cela reste sous 20 ms.

## 7. Limites

- Le minimum n'est garanti que jusqu'à 5 nombres.
- Au-delà, les K sont des mesures sur ce corpus, pas des garanties.
- `pa`, `pb` et les rotations coûtent O(n) à cause de la représentation.
  Une pile circulaire les rendrait O(1), mais le code serait plus compliqué.
