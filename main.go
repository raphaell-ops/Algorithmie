// push_swap : affiche les commandes qui trient les nombres donnés.
//
//	go run . 3 2 1
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
	// Si l'écriture échoue (sortie fermée, disque plein...), statut 3.
	if _, err := fmt.Print(sortie); err != nil {
		fmt.Fprintln(os.Stderr, "erreur d'écriture :", err)
		os.Exit(3)
	}
}

// run lit les nombres et renvoie le texte à afficher.
// ok vaut false si l'entrée est invalide.
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
