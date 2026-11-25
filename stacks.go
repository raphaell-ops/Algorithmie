package main

import (
	"errors"
	"fmt"
)

type Stacks struct {
	A      []int64
	B      []int64
	Compte int
}

var ErrUnknown = errors.New("instruction inconnue")

var Commands = []string{"sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr"}

func copier(pile []int64) []int64 {
	copie := make([]int64, len(pile))
	for i := 0; i < len(pile); i++ {
		copie[i] = pile[i]
	}
	return copie
}

func NewStacks(valeurs []int64) *Stacks {
	return &Stacks{A: copier(valeurs), B: []int64{}}
}

func (s *Stacks) Clone() *Stacks {
	return &Stacks{A: copier(s.A), B: copier(s.B), Compte: s.Compte}
}

func (s *Stacks) Key() string {
	return fmt.Sprint(s.A, s.B)
}

func (s *Stacks) IsSorted() bool {
	if len(s.B) != 0 {
		return false
	}
	for i := 1; i < len(s.A); i++ {
		if s.A[i-1] >= s.A[i] {
			return false
		}
	}
	return true
}

func echanger(pile []int64) {
	if len(pile) < 2 {
		return
	}
	temp := pile[0]
	pile[0] = pile[1]
	pile[1] = temp
}

func pousser(source []int64, destination []int64) ([]int64, []int64) {
	if len(source) == 0 {
		return source, destination
	}
	haut := source[0]
	source = source[1:]
	destination = append([]int64{haut}, destination...)
	return source, destination
}

func tourner(pile []int64) {
	if len(pile) < 2 {
		return
	}
	haut := pile[0]
	for i := 0; i < len(pile)-1; i++ {
		pile[i] = pile[i+1]
	}
	pile[len(pile)-1] = haut
}

func tournerInverse(pile []int64) {
	if len(pile) < 2 {
		return
	}
	bas := pile[len(pile)-1]
	for i := len(pile) - 1; i > 0; i-- {
		pile[i] = pile[i-1]
	}
	pile[0] = bas
}

func (s *Stacks) Exec(commande string) error {
	switch commande {
	case "sa":
		echanger(s.A)
	case "sb":
		echanger(s.B)
	case "ss":
		echanger(s.A)
		echanger(s.B)
	case "pa":
		s.B, s.A = pousser(s.B, s.A)
	case "pb":
		s.A, s.B = pousser(s.A, s.B)
	case "ra":
		tourner(s.A)
	case "rb":
		tourner(s.B)
	case "rr":
		tourner(s.A)
		tourner(s.B)
	case "rra":
		tournerInverse(s.A)
	case "rrb":
		tournerInverse(s.B)
	case "rrr":
		tournerInverse(s.A)
		tournerInverse(s.B)
	default:
		return ErrUnknown
	}
	s.Compte++
	return nil
}
