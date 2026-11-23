package main

import (
	"errors"
	"strconv"
	"strings"
)

// Les trois erreurs du parseur.
var (
	ErrSyntax    = errors.New("erreur de syntaxe")
	ErrOverflow  = errors.New("dépassement numérique")
	ErrDuplicate = errors.New("doublon")
)

func validSyntax(s string) bool {
	i := 0
	if i < len(s) && (s[i] == '+' || s[i] == '-') {
		i++
	}
	if i == len(s) {
		return false
	}
	for i < len(s) {
		if s[i] < '0' || s[i] > '9' {
			return false
		}
		i++
	}
	return true
}

// ParseNumber convertit un jeton en int64.
func ParseNumber(input string) (int64, bool, error) {
	s := strings.TrimSpace(input)
	if s == "" {
		return 0, true, nil
	}
	if !validSyntax(s) {
		return 0, false, ErrSyntax
	}
	n, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return 0, false, ErrOverflow
	}
	return n, false, nil
}

// ParseArgs lit tous les arguments du programme.
func ParseArgs(args []string) ([]int64, error) {
	values := []int64{}
	for _, arg := range args {
		tokens := strings.Fields(arg)
		if len(tokens) == 0 {
			return nil, ErrSyntax
		}
		for _, tok := range tokens {
			n, _, err := ParseNumber(tok)
			if err != nil {
				return nil, err
			}
			for _, v := range values {
				if v == n {
					return nil, ErrDuplicate
				}
			}
			values = append(values, n)
		}
	}
	return values, nil
}
