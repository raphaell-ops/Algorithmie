package main

const Budget = 100000

type candidate struct {
	state *Stacks
	cmds  []string
}

func BruteForce(values []int64) (cmds []string, found bool, explored int) {
	start := NewStacks(values)
	if start.IsSorted() {
		return []string{}, true, 1
	}

	queue := []candidate{{state: start, cmds: []string{}}}
	seen := map[string]bool{start.Key(): true}

	for i := 0; i < len(queue); i++ {
		current := queue[i]
		for _, c := range Commands {
			next := current.state.Clone()
			next.Exec(c)

			key := next.Key()
			if seen[key] {
				continue
			}
			seen[key] = true

			path := make([]string, len(current.cmds))
			copy(path, current.cmds)
			path = append(path, c)

			if next.IsSorted() {
				return path, true, len(seen)
			}
			if len(seen) >= Budget {
				return nil, false, len(seen)
			}
			queue = append(queue, candidate{state: next, cmds: path})
		}
	}
	return nil, false, len(seen)
}
