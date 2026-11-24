package main

import (
	"fmt"
	"os"
)

func main() {
	sortie, ok := run(os.Args[1:])
	if !ok {
		fmt.Fprintln(os.Stderr, "Error")
		os.Exit(1)
	}
	if _, err := fmt.Print(sortie); err != nil {
		fmt.Fprintln(os.Stderr, "erreur d'écriture :", err)
		os.Exit(3)
	}
}

func run(args []string) (string, bool) {
	values, err := ParseArgs(args)
	if err != nil {
		return "", false
	}
	sortie := ""
	for _, c := range Solve(values) {
		sortie += c + "\n"
	}
	return sortie, true
}
