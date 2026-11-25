package main

import "errors"

var (
	ErrNotSorted = errors.New("A n'est pas triée")
	ErrBNotEmpty = errors.New("B n'est pas vide")
	ErrLostValue = errors.New("une valeur a disparu")
)

func Verify(depart []int64, commandes []string) (int, error) {
	piles := NewStacks(depart)
	for _, c := range commandes {
		err := piles.Exec(c)
		if err != nil {
			return 0, err
		}
	}
	if len(piles.B) != 0 {
		return 0, ErrBNotEmpty
	}
	if !piles.IsSorted() {
		return 0, ErrNotSorted
	}
	if len(piles.A) != len(depart) {
		return 0, ErrLostValue
	}
	return len(commandes), nil
}
