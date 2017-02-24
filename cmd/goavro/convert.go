package main

import (
	"fmt"
	"log"
	"strings"

	convert "github.com/aerokite/go-avro-convert/pkg"
	"github.com/spf13/cobra"
)

func conversion(text string) {
	converted, err := convert.Convert(text)
	if err != nil {
		log.Fatalln(err)
	}
	fmt.Println(converted)
}

func newCmdGovro() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "convert",
		Short: "text for conversion",
		Run: func(cmd *cobra.Command, args []string) {
			if len(args) > 0 {
				text := strings.Join(args, " ")
				conversion(text)
			} else {
				fmt.Println("Provide text to convert")
			}
		},
	}
	return cmd
}
