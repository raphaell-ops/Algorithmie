package main

import (
	"math/rand"
	"reflect"
	"sort"
	"testing"
	"time"
)

func TestParseArgsValides(t *testing.T) {
	tests := []struct {
		args []string
		want []int64
	}{
		{[]string{}, []int64{}},
		{[]string{"3", "1", "2"}, []int64{3, 1, 2}},
		{[]string{"3 1", "2"}, []int64{3, 1, 2}},
		{[]string{"+5", "-3", "007"}, []int64{5, -3, 7}},
		{[]string{"9223372036854775807"}, []int64{9223372036854775807}},
		{[]string{"-9223372036854775808"}, []int64{-9223372036854775808}},
	}
	for _, tt := range tests {
		got, err := ParseArgs(tt.args)
		if err != nil || !reflect.DeepEqual(got, tt.want) {
			t.Errorf("ParseArgs(%q) = %v, %v ; attendu %v", tt.args, got, err, tt.want)
		}
	}
}

func TestParseArgsErreurs(t *testing.T) {
	tests := []struct {
		args []string
		want error
	}{
		{[]string{"12a"}, ErrSyntax},
		{[]string{"-"}, ErrSyntax},
		{[]string{"1.5"}, ErrSyntax},
		{[]string{""}, ErrSyntax},
		{[]string{"   "}, ErrSyntax},
		{[]string{"99999999999999999999x"}, ErrSyntax},
		{[]string{"9223372036854775808"}, ErrOverflow},
		{[]string{"-9223372036854775809"}, ErrOverflow},
		{[]string{"1", "1"}, ErrDuplicate},
		{[]string{"1", "+1"}, ErrDuplicate},
		{[]string{"1", "01"}, ErrDuplicate},
		{[]string{"0", "-0"}, ErrDuplicate},
	}
	for _, tt := range tests {
		got, err := ParseArgs(tt.args)
		if got != nil || err != tt.want {
			t.Errorf("ParseArgs(%q) = %v, %v ; attendu l'erreur %v", tt.args, got, err, tt.want)
		}
	}
}

func TestCommandes(t *testing.T) {
	tests := []struct {
		cmd   string
		wantA []int64
		wantB []int64
	}{
		{"sa", []int64{3, 8, 6}, []int64{4, 1}},
		{"sb", []int64{8, 3, 6}, []int64{1, 4}},
		{"ss", []int64{3, 8, 6}, []int64{1, 4}},
		{"pa", []int64{4, 8, 3, 6}, []int64{1}},
		{"pb", []int64{3, 6}, []int64{8, 4, 1}},
		{"ra", []int64{3, 6, 8}, []int64{4, 1}},
		{"rb", []int64{8, 3, 6}, []int64{1, 4}},
		{"rr", []int64{3, 6, 8}, []int64{1, 4}},
		{"rra", []int64{6, 8, 3}, []int64{4, 1}},
		{"rrb", []int64{8, 3, 6}, []int64{1, 4}},
		{"rrr", []int64{6, 8, 3}, []int64{1, 4}},
	}
	for _, tt := range tests {
		s := NewStacks([]int64{8, 3, 6})
		s.B = []int64{4, 1}
		s.Exec(tt.cmd)
		if !reflect.DeepEqual(s.A, tt.wantA) || !reflect.DeepEqual(s.B, tt.wantB) {
			t.Errorf("%s : A=%v B=%v ; attendu A=%v B=%v", tt.cmd, s.A, s.B, tt.wantA, tt.wantB)
		}
		if s.Compte != 1 {
			t.Errorf("%s : score %d, attendu 1", tt.cmd, s.Compte)
		}
	}
}

func TestCommandesCasLimites(t *testing.T) {
	tests := []struct {
		cmd          string
		a, b         []int64
		wantA, wantB []int64
	}{
		{"sa", []int64{}, []int64{}, []int64{}, []int64{}},
		{"sa", []int64{1}, []int64{}, []int64{1}, []int64{}},
		{"pa", []int64{1}, []int64{}, []int64{1}, []int64{}},
		{"pb", []int64{}, []int64{2}, []int64{}, []int64{2}},
		{"ra", []int64{1}, []int64{}, []int64{1}, []int64{}},
		{"rra", []int64{}, []int64{}, []int64{}, []int64{}},
		{"ss", []int64{1, 2}, []int64{3}, []int64{2, 1}, []int64{3}},
		{"rr", []int64{}, []int64{1, 2, 3}, []int64{}, []int64{2, 3, 1}},
		{"rrr", []int64{1, 2, 3}, []int64{}, []int64{3, 1, 2}, []int64{}},
	}
	for _, tt := range tests {
		s := NewStacks(tt.a)
		s.B = tt.b
		s.Exec(tt.cmd)
		if !reflect.DeepEqual(s.A, tt.wantA) || !reflect.DeepEqual(s.B, tt.wantB) {
			t.Errorf("%s sur A=%v B=%v : obtenu A=%v B=%v", tt.cmd, tt.a, tt.b, s.A, s.B)
		}
		if s.Compte != 1 {
			t.Errorf("%s : score %d, attendu 1", tt.cmd, s.Compte)
		}
	}
}

func TestCommandeInconnue(t *testing.T) {
	s := NewStacks([]int64{2, 1})
	if err := s.Exec("xx"); err != ErrUnknown {
		t.Errorf("erreur attendue, obtenu %v", err)
	}
	if !reflect.DeepEqual(s.A, []int64{2, 1}) || s.Compte != 0 {
		t.Error("une commande inconnue a modifié les piles ou le score")
	}
}

func TestEntreeConservee(t *testing.T) {
	entree := []int64{3, 1, 2}
	s := NewStacks(entree)
	s.Exec("sa")
	s.Exec("ra")
	if !reflect.DeepEqual(entree, []int64{3, 1, 2}) {
		t.Errorf("entrée modifiée : %v", entree)
	}
}

func TestCloneStable(t *testing.T) {
	s := NewStacks([]int64{1, 2, 3})
	copie := s.Clone()
	s.Exec("ra")
	s.Exec("pb")
	if !reflect.DeepEqual(copie.A, []int64{1, 2, 3}) || len(copie.B) != 0 {
		t.Errorf("la copie a changé : A=%v B=%v", copie.A, copie.B)
	}
}

func TestVerifyOK(t *testing.T) {
	if _, err := Verify([]int64{}, []string{}); err != nil {
		t.Error("entrée vide :", err)
	}
	if _, err := Verify([]int64{1, 2, 3}, []string{}); err != nil {
		t.Error("déjà trié :", err)
	}
	if k, err := Verify([]int64{3, 2, 1}, []string{"sa", "rra"}); err != nil || k != 2 {
		t.Error("sa rra :", k, err)
	}
}

func TestVerifyErreurs(t *testing.T) {
	tests := []struct {
		nom    string
		values []int64
		cmds   []string
		want   error
	}{
		{"commande inconnue", []int64{2, 1}, []string{"sa", "xx"}, ErrUnknown},
		{"suite incomplète", []int64{3, 2, 1}, []string{"sa"}, ErrNotSorted},
		{"B pas vide à la fin", []int64{1, 2, 3}, []string{"pb"}, ErrBNotEmpty},
		{"A pas triée à la fin", []int64{1, 2, 3}, []string{"ra"}, ErrNotSorted},
	}
	for _, tt := range tests {
		if _, err := Verify(tt.values, tt.cmds); err != tt.want {
			t.Errorf("%s : obtenu %v, attendu %v", tt.nom, err, tt.want)
		}
	}
}

func TestBruteForce(t *testing.T) {
	tests := []struct {
		values []int64
		k      int
	}{
		{[]int64{1, 2, 3}, 0},
		{[]int64{2, 1}, 1},
		{[]int64{3, 1, 2}, 1},
		{[]int64{2, 3, 1}, 1},
		{[]int64{3, 2, 1}, 2},
	}
	for _, tt := range tests {
		cmds, found, _ := BruteForce(tt.values)
		if !found || len(cmds) != tt.k {
			t.Errorf("%v : %v (trouvé=%v), attendu %d commandes", tt.values, cmds, found, tt.k)
		}
	}
}

func TestBruteForceToutesPermutations(t *testing.T) {
	for n := 1; n <= 5; n++ {
		perms := permutations(n)
		maxK, maxEtats := 0, 0
		debut := time.Now()
		for _, p := range perms {
			cmds, found, etats := BruteForce(p)
			if etats > maxEtats {
				maxEtats = etats
			}
			if !found {
				t.Fatalf("%v : pas de solution", p)
			}
			if _, err := Verify(p, cmds); err != nil {
				t.Fatalf("%v : suite invalide : %v", p, err)
			}
			if len(cmds) > maxK {
				maxK = len(cmds)
			}
		}
		t.Logf("n=%d : %d permutations résolues, au pire %d commandes, au pire %d états gardés, durée totale %v",
			n, len(perms), maxK, maxEtats, time.Since(debut).Round(time.Microsecond))
	}
}

func permutations(n int) [][]int64 {
	if n == 0 {
		return [][]int64{{}}
	}
	result := [][]int64{}
	for _, p := range permutations(n - 1) {
		for pos := 0; pos <= len(p); pos++ {
			q := []int64{}
			q = append(q, p[:pos]...)
			q = append(q, int64(n))
			q = append(q, p[pos:]...)
			result = append(result, q)
		}
	}
	return result
}

var entrees = [][]int64{
	{},
	{42},
	{1, 2, 3, 4, 5, 6},
	{6, 5, 4, 3, 2, 1},
	{1, 2, 4, 3, 5, 6},
	{-5, 100, 0, -42, 7, 3},
	{9223372036854775807, -9223372036854775808, 0, 5, -5, 1},
}

func TestStrategiesValides(t *testing.T) {
	strategies := []struct {
		nom string
		f   func([]int64) []string
	}{
		{"SelectionV0", SelectionV0},
		{"SelectionV1", SelectionV1},
		{"Radix", Radix},
		{"Solve", Solve},
	}
	for _, s := range strategies {
		for _, e := range entrees {
			if _, err := Verify(e, s.f(e)); err != nil {
				t.Errorf("%s sur %v : %v", s.nom, e, err)
			}
		}
		if len(s.f([]int64{})) != 0 || len(s.f([]int64{7})) != 0 || len(s.f([]int64{1, 2, 3})) != 0 {
			t.Errorf("%s : des commandes pour une entrée déjà triée", s.nom)
		}
	}
}

func melange(r *rand.Rand, n int) []int64 {
	values := make([]int64, n)
	for i, v := range r.Perm(n) {
		values[i] = int64(v)
	}
	return values
}

func famille(nom string, n int) [][]int64 {
	r := rand.New(rand.NewSource(int64(n)))
	entrees := [][]int64{}
	switch nom {
	case "aléatoire":
		for i := 0; i < 20; i++ {
			entrees = append(entrees, melange(r, n))
		}
	case "trié":
		e := make([]int64, n)
		for i := range e {
			e[i] = int64(i)
		}
		entrees = append(entrees, e)
	case "inversé":
		e := make([]int64, n)
		for i := range e {
			e[i] = int64(n - 1 - i)
		}
		entrees = append(entrees, e)
	case "presque trié":
		for k := 0; k < 5; k++ {
			e := make([]int64, n)
			for i := range e {
				e[i] = int64(i)
			}
			for j := 0; j < 5; j++ {
				p := r.Intn(n - 1)
				e[p], e[p+1] = e[p+1], e[p]
			}
			entrees = append(entrees, e)
		}
	}
	return entrees
}

func TestComparaison(t *testing.T) {
	strategies := []struct {
		nom string
		f   func([]int64) []string
	}{
		{"SelectionV0", SelectionV0},
		{"SelectionV1", SelectionV1},
		{"Radix", Radix},
		{"Solve", Solve},
	}
	for _, n := range []int{100, 500} {
		for _, fam := range []string{"aléatoire", "trié", "inversé", "presque trié"} {
			entrees := famille(fam, n)
			for _, s := range strategies {
				ks := []int{}
				debut := time.Now()
				for _, e := range entrees {
					cmds := s.f(e)
					if _, err := Verify(e, cmds); err != nil {
						t.Fatalf("%s invalide sur %s : %v", s.nom, fam, err)
					}
					ks = append(ks, len(cmds))
				}
				duree := time.Since(debut) / time.Duration(len(entrees))
				sort.Ints(ks)
				t.Logf("n=%-3d %-12s %-11s K médian=%-6d K max=%-6d durée moyenne=%v",
					n, fam, s.nom, ks[len(ks)/2], ks[len(ks)-1], duree.Round(time.Microsecond))
			}
		}
	}
}

func TestProgramme(t *testing.T) {
	tests := []struct {
		args   []string
		sortie string
		ok     bool
	}{
		{[]string{}, "", true},
		{[]string{"1", "2", "3"}, "", true},
		{[]string{"2", "1"}, "sa\n", true},
		{[]string{"1", "abc"}, "", false},
		{[]string{"1", "+1"}, "", false},
	}
	for _, tt := range tests {
		sortie, ok := run(tt.args)
		if sortie != tt.sortie || ok != tt.ok {
			t.Errorf("run(%q) = (%q, %v), attendu (%q, %v)", tt.args, sortie, ok, tt.sortie, tt.ok)
		}
	}
}
