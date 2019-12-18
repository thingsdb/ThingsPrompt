# ThingsPrompt

Shell client for ThingsDB


## Installation

Using pip:

```shell
pip install thingsprompt
```

Or, clone this project and use the setup

```shell
python setup.py install
```

## Example usage

```shell
thingsprompt -n localhost -u admin -p pass


127.0.0.1:9200 (@thingsdb)> new_collection('my_collection');
127.0.0.1:9200 (@thingsdb)> @:my_collection
127.0.0.1:9200 (@:my_collection)> .greet = "Hello world!";

"Hello world!"
```

## Arguments

```
  -h, --help            show help message and exit
  --node NODE, -n NODE  node address
  --port PORT           TCP port where the node is listening on for API calls
  --user USER, -u USER  user name
  --password PASSWORD, -p PASSWORD
                        password, will be prompted if not given
  --token TOKEN, -t TOKEN
                        token key
  --scope SCOPE, -s SCOPE
                        set the initial scope
  --timeout TIMEOUT     connect and query timeout in second
  --ssl                 enable secure connection (SSL/TLS)
  --version             print version and exit
```

## Special commands

command        | description
---------------|----------------------
`?`            | Show help.
`@scope`       | Switch to another scope, for example: `@:stuff`
`@scope query` | Run a single query in a given scope, for example `@n node_info();`
`CTRL + n`     | Insert a new line