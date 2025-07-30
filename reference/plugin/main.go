package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	if len(os.Args) < 2 || os.Args[1] == "--help" || os.Args[1] == "-h" {
		printUsage()
		os.Exit(0)
	}

	for _, name := range os.Args[1:] {
		if strings.HasPrefix(name, "-") {
			fmt.Fprintf(os.Stderr, "Unrecognized option: %s\n", name)
			printUsage()
			os.Exit(1)
		}

		envKey := fmt.Sprintf("DST_%s", strings.ToUpper(name))
		path := os.Getenv(envKey)
		if path == "" {
			fmt.Fprintf(os.Stderr, "Missing env var: %s\n", envKey)
			continue
		}

		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading %s (%s): %v\n", name, path, err)
			continue
		}

		fmt.Printf("----- [%s] %s -----\n%s\n", name, path, string(data))
	}
}

func printUsage() {
	fmt.Println("Usage: myapp <name1> [<name2> ...]")
	fmt.Println("  1. Downloads files specified in the configuration.")
	fmt.Println("  2. Reads environment variables prefixed with DST_ and prints their contents.")
	fmt.Println("Example: myapp file1 file2")
}
