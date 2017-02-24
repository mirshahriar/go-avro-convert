package pkg

import (
	translate "github.com/aerokite/go-google-translate/pkg"
	avro "github.com/sadlil/go-avro-phonetic"
)

func Convert(text string) (string, error) {
	parsedText, err := avro.Parse(text)
	if err != nil {
		return "", err
	}

	req := translate.TranslateRequest{
		SourceLang: "bn",
		TargetLang: "en",
		Text:       parsedText,
	}
	translatedText, err := translate.Translate(req)
	if err != nil {
		return "", err
	}

	return translatedText, nil
}
