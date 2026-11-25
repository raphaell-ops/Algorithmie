package main

func faire(piles *Stacks, commandes []string, c string) []string {
	piles.Exec(c)
	return append(commandes, c)
}

func positionMin(pile []int64) int {
	position := 0
	for i := 1; i < len(pile); i++ {
		if pile[i] < pile[position] {
			position = i
		}
	}
	return position
}

func SelectionV0(valeurs []int64) []string {
	piles := NewStacks(valeurs)
	commandes := []string{}
	if piles.IsSorted() {
		return commandes
	}
	for len(piles.A) > 0 {
		position := positionMin(piles.A)
		for i := 0; i < position; i++ {
			commandes = faire(piles, commandes, "ra")
		}
		commandes = faire(piles, commandes, "pb")
	}
	for len(piles.B) > 0 {
		commandes = faire(piles, commandes, "pa")
	}
	return commandes
}

func SelectionV1(valeurs []int64) []string {
	piles := NewStacks(valeurs)
	commandes := []string{}
	if piles.IsSorted() {
		return commandes
	}
	for len(piles.A) > 0 {
		position := positionMin(piles.A)
		if position <= len(piles.A)/2 {
			for i := 0; i < position; i++ {
				commandes = faire(piles, commandes, "ra")
			}
		} else {
			for i := 0; i < len(piles.A)-position; i++ {
				commandes = faire(piles, commandes, "rra")
			}
		}
		commandes = faire(piles, commandes, "pb")
	}
	for len(piles.B) > 0 {
		commandes = faire(piles, commandes, "pa")
	}
	return commandes
}

func rang(valeurs []int64) []int64 {
	rangs := make([]int64, len(valeurs))
	for i := 0; i < len(valeurs); i++ {
		for j := 0; j < len(valeurs); j++ {
			if valeurs[j] < valeurs[i] {
				rangs[i]++
			}
		}
	}
	return rangs
}

func Radix(valeurs []int64) []string {
	piles := NewStacks(rang(valeurs))
	commandes := []string{}
	taille := len(piles.A)
	puissance := int64(1)
	for !piles.IsSorted() {
		for i := 0; i < taille; i++ {
			bit := (piles.A[0] / puissance) % 2
			if bit == 0 {
				commandes = faire(piles, commandes, "pb")
			} else {
				commandes = faire(piles, commandes, "ra")
			}
		}
		for len(piles.B) > 0 {
			commandes = faire(piles, commandes, "pa")
		}
		puissance = puissance * 2
	}
	return commandes
}

func Solve(valeurs []int64) []string {
	if len(valeurs) <= 5 {
		cmds, trouve, _ := BruteForce(valeurs)
		if trouve {
			return cmds
		}
	}
	parSelection := SelectionV1(valeurs)
	parRadix := Radix(valeurs)
	if len(parSelection) <= len(parRadix) {
		return parSelection
	}
	return parRadix
}
