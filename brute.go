package main

const Budget = 100000

type etat struct {
	piles     *Stacks
	commandes []string
}

func dejaVu(vus []string, cle string) bool {
	for _, v := range vus {
		if v == cle {
			return true
		}
	}
	return false
}

func BruteForce(valeurs []int64) (cmds []string, found bool, explored int) {
	depart := NewStacks(valeurs)
	if depart.IsSorted() {
		return []string{}, true, 1
	}

	file := []etat{{piles: depart, commandes: []string{}}}
	vus := []string{depart.Key()}

	for i := 0; i < len(file); i++ {
		actuel := file[i]
		for _, c := range Commands {
			suivant := actuel.piles.Clone()
			suivant.Exec(c)

			cle := suivant.Key()
			if dejaVu(vus, cle) {
				continue
			}
			vus = append(vus, cle)

			chemin := make([]string, len(actuel.commandes))
			copy(chemin, actuel.commandes)
			chemin = append(chemin, c)

			if suivant.IsSorted() {
				return chemin, true, len(vus)
			}
			if len(vus) >= Budget {
				return nil, false, len(vus)
			}
			file = append(file, etat{piles: suivant, commandes: chemin})
		}
	}
	return nil, false, len(vus)
}
