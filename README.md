# naanj

Reflection of NAAN registry, in json.

[![Screen shot animation](https://i.imgur.com/O1lQFFV.gif)](https://vimeo.com/535589766)

`Naanj` is a python script that generates a [JSON translation](data/naanj.json)
of the NAAN authority [public ANVL source](https://n2t.net/e/pub/naan_registry.txt) and 
optionally tests connectivity to the referenced resources.

A web viewer is available at [datadavev.github.io/naanj](https://datadavev.github.io/naanj).

The JSON translation file is updated by a GitHub action every day at 
approximately 05:05 UTC. 

## Installation

`naanj` can be installed and run locally. The recommended procedure for simply 
installing the command line tool is with [`pipx`](https://github.com/pipxproject/pipx):

```
pipx install git+https://github.com/datadavev/naanj.git
```

The `naanj` command is then available from the terminal:

```
Usage: naanj [OPTIONS] [DESTINATION]

Options:
  -n, --naans TEXT  ANVL Source URL
  -p, --progress    Show progress when testing (implies -t)
  -t, --test        Test URLs listed as location
  --verbosity TEXT  Specify logging level  [default: INFO]
  --help            Show this message and exit.
```

If the `DESTINATION` is not specified, output is to `stdout`.

## Development

`naanj` uses [`poetry`](https://python-poetry.org/) for dependency 
management. Development within a python virtual environment is 
recommended. To setup development:

```
git clone https://github.com/datadavev/naanj.git
cd naanj
poetry install
```





