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

func syntaxeValide(texte string) bool {
	debut := 0
	if texte[0] == '+' || texte[0] == '-' {
		debut = 1
	}
	if debut == len(texte) {
		return false
	}
	for i := debut; i < len(texte); i++ {
		if texte[i] < '0' || texte[i] > '9' {
			return false
		}
	}
	return true
}

func ParseNumber(texte string) (int64, error) {
	if !syntaxeValide(texte) {
		return 0, ErrSyntax
	}
	nombre, err := strconv.ParseInt(texte, 10, 64)
	if err != nil {
		return 0, ErrOverflow
	}
	return nombre, nil
}

func ParseArgs(args []string) ([]int64, error) {
	valeurs := []int64{}
	for _, arg := range args {
		mots := strings.Fields(arg)
		if len(mots) == 0 {
			return nil, ErrSyntax
		}
		for _, mot := range mots {
			nombre, err := ParseNumber(mot)
			if err != nil {
				return nil, err
			}
			for _, v := range valeurs {
				if v == nombre {
					return nil, ErrDuplicate
				}
			}
			valeurs = append(valeurs, nombre)
		}
	}
	return valeurs, nil
}
