<meta name='keywords' content='avro phonetic, go avro, phonetic translation, bangla to english, goavro'>


# go-avro-convert

Translate phonetic Bangla to English.

# Overview

`go-avro-convert` provides a `go` package to convert your phonetic Bangla to its translated English.

# Installation

```sh
$ go get -u -v github.com/aerokite/go-avro-convert/...
```

# Usage

```go
package any

import (
        "fmt"
        "log"

        convert "github.com/aerokite/go-avro-convert/pkg"
)

func main(){
        text := "Ami Banglay gan gai."
        converted, err := convert.Convert(text)
        if err != nil {
                log.Fatalln(err)
        }
        fmt.Println(converted) // I sing in Bangla.
}
```

# CLI

This library provides a command line interface to make this conversion.

### Install

```sh
$ go get -u -v github.com/aerokite/go-avro-convert/cmd/goavro
$ go install github.com/aerokite/go-avro-convert/cmd/goavro
```

### Usage

```sh
$ goavro convert "Ami Bangla ke valobasi."
I love Bengali.
```

# License

Copyright (c) 2017 Mir Shahriar

Licensed under MIT Licence.
