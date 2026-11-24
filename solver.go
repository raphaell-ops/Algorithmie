package main

func do(s *Stacks, cmds []string, c string) []string {
	s.Exec(c)
	return append(cmds, c)
}

func minPosition(pile []int64) int {
	pos := 0
	for i := 1; i < len(pile); i++ {
		if pile[i] < pile[pos] {
			pos = i
		}
	}
	return pos
}

func SelectionV0(values []int64) []string {
	s := NewStacks(values)
	cmds := []string{}
	if s.IsSorted() {
		return cmds
	}
	for len(s.A) > 0 {
		pos := minPosition(s.A)
		for i := 0; i < pos; i++ {
			cmds = do(s, cmds, "ra")
		}
		cmds = do(s, cmds, "pb")
	}
	for len(s.B) > 0 {
		cmds = do(s, cmds, "pa")
	}
	return cmds
}

func SelectionV1(values []int64) []string {
	s := NewStacks(values)
	cmds := []string{}
	if s.IsSorted() {
		return cmds
	}
	for len(s.A) > 0 {
		pos := minPosition(s.A)
		if pos <= len(s.A)/2 {
			for i := 0; i < pos; i++ {
				cmds = do(s, cmds, "ra")
			}
		} else {
			for i := 0; i < len(s.A)-pos; i++ {
				cmds = do(s, cmds, "rra")
			}
		}
		cmds = do(s, cmds, "pb")
	}
	for len(s.B) > 0 {
		cmds = do(s, cmds, "pa")
	}
	return cmds
}

func rank(values []int64) []int64 {
	r := make([]int64, len(values))
	for i, v := range values {
		for _, w := range values {
			if w < v {
				r[i]++
			}
		}
	}
	return r
}

func Radix(values []int64) []string {
	s := NewStacks(rank(values))
	cmds := []string{}
	n := len(s.A)
	puissance := int64(1)
	for !s.IsSorted() {
		for i := 0; i < n; i++ {
			chiffre := (s.A[0] / puissance) % 2
			if chiffre == 0 {
				cmds = do(s, cmds, "pb")
			} else {
				cmds = do(s, cmds, "ra")
			}
		}
		for len(s.B) > 0 {
			cmds = do(s, cmds, "pa")
		}
		puissance *= 2
	}
	return cmds
}

func Solve(values []int64) []string {
	if len(values) <= 5 {
		cmds, found, _ := BruteForce(values)
		if found {
			return cmds
		}
	}
	a := SelectionV1(values)
	b := Radix(values)
	if len(a) <= len(b) {
		return a
	}
	return b
}
