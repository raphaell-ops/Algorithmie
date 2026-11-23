package main

import "errors"

var (
	ErrNotSorted = errors.New("A n'est pas triée")
	ErrBNotEmpty = errors.New("B n'est pas vide")
	ErrLostValue = errors.New("une valeur a disparu")
)

func Verify(original []int64, cmds []string) (int, error) {
	s := NewStacks(original)
	for _, c := range cmds {
		if err := s.Exec(c); err != nil {
			return 0, err
		}
	}
	if len(s.B) != 0 {
		return 0, ErrBNotEmpty
	}
	if !s.IsSorted() {
		return 0, ErrNotSorted
	}
	if len(s.A) != len(original) {
		return 0, ErrLostValue
	}
	for _, v := range original {
		found := false
		for _, x := range s.A {
			if x == v {
				found = true
			}
		}
		if !found {
			return 0, ErrLostValue
		}
	}
	return len(cmds), nil
}
