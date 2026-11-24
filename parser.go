package main

import (
	"errors"
	"strconv"
	"strings"
)

var (
	ErrSyntax    = errors.New("erreur de syntaxe")
	ErrOverflow  = errors.New("dépassement numérique")
	ErrDuplicate = errors.New("doublon")
)

func validSyntax(s string) bool {
	i := 0
	if s[0] == '+' || s[0] == '-' {
		i++
	}
	if i == len(s) {
		return false
	}
	for ; i < len(s); i++ {
		if s[i] < '0' || s[i] > '9' {
			return false
		}
	}
	return true
}

func ParseNumber(s string) (int64, error) {
	if !validSyntax(s) {
		return 0, ErrSyntax
	}
	n, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return 0, ErrOverflow
	}
	return n, nil
}

func ParseArgs(args []string) ([]int64, error) {
	values := []int64{}
	for _, arg := range args {
		tokens := strings.Fields(arg)
		if len(tokens) == 0 {
			return nil, ErrSyntax
		}
		for _, tok := range tokens {
			n, err := ParseNumber(tok)
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
