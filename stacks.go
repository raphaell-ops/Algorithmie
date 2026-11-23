package main

import (
	"errors"
	"fmt"
)

type Stacks struct {
	A     []int64
	B     []int64
	Count int
}

var ErrUnknown = errors.New("instruction inconnue")

// Les 11 commandes du jeu.
var Commands = []string{"sa", "sb", "ss", "pa", "pb", "ra", "rb", "rr", "rra", "rrb", "rrr"}

// NewStacks crée l'état de départ.
func NewStacks(values []int64) *Stacks {
	a := make([]int64, len(values))
	copy(a, values)
	return &Stacks{A: a, B: []int64{}}
}

// Clone fait une copie complète des piles.
func (s *Stacks) Clone() *Stacks {
	a := make([]int64, len(s.A))
	copy(a, s.A)
	b := make([]int64, len(s.B))
	copy(b, s.B)
	return &Stacks{A: a, B: b, Count: s.Count}
}

// Key renvoie un texte qui représente l'état, par exemple "[2 1] [3]".
func (s *Stacks) Key() string {
	return fmt.Sprint(s.A, s.B)
}

// IsSorted vérifie l'état final : B est vide et A est croissante.
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

// swap échange les deux premiers éléments.
func swap(s []int64) {
	if len(s) < 2 {
		return
	}
	s[0], s[1] = s[1], s[0]
}

// push prend le sommet de from et le met au sommet de to.
func push(from, to *[]int64) {
	if len(*from) == 0 {
		return
	}
	top := (*from)[0]
	*from = (*from)[1:]
	*to = append([]int64{top}, *to...)
}

// rotate met le sommet au fond.
func rotate(s []int64) {
	if len(s) < 2 {
		return
	}
	top := s[0]
	for i := 0; i < len(s)-1; i++ {
		s[i] = s[i+1]
	}
	s[len(s)-1] = top
}

// reverseRotate met le fond au sommet (rien si moins de 2).
func reverseRotate(s []int64) {
	if len(s) < 2 {
		return
	}
	bottom := s[len(s)-1]
	for i := len(s) - 1; i > 0; i-- {
		s[i] = s[i-1]
	}
	s[0] = bottom
}

// Exec applique une commande.
func (s *Stacks) Exec(cmd string) error {
	switch cmd {
	case "sa":
		swap(s.A)
	case "sb":
		swap(s.B)
	case "ss":
		swap(s.A)
		swap(s.B)
	case "pa":
		push(&s.B, &s.A)
	case "pb":
		push(&s.A, &s.B)
	case "ra":
		rotate(s.A)
	case "rb":
		rotate(s.B)
	case "rr":
		rotate(s.A)
		rotate(s.B)
	case "rra":
		reverseRotate(s.A)
	case "rrb":
		reverseRotate(s.B)
	case "rrr":
		reverseRotate(s.A)
		reverseRotate(s.B)
	default:
		return ErrUnknown
	}
	s.Count++
	return nil
}
