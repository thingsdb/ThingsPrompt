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
things-prompt -n localhost -u admin -p pass


127.0.0.1:9200 (@thingsdb)> new_collection('my_collection');
127.0.0.1:9200 (@thingsdb)> @:my_collection
127.0.0.1:9200 (@:my_collection)> .greet = "Hello world!";

"Hello world!"
```

## Example import/export

```shell
# Export the "stuff" collection to a filename
things-prompt -n localhost -u admin -p pass -s //stuff export /tmp/dump.mp

# Import the file into a new collection "clone"
# ThingsDB prompt will automatically create the collection if it does not exist
things-prompt -n localhost -u admin -p pass -s //clone import /tmp/dump.mp
```

## Help

```
usage: things-prompt [-h] [--node NODE] [--port PORT] [--user USER]
                     [--password PASSWORD] [--token TOKEN] [--scope SCOPE]
                     [--timeout TIMEOUT] [--ssl] [--hide-connection-info]
                     [--style {dracula,monokai,colorful,friendly,vim,none}]
                     [--version]
                     {export,import} ...

positional arguments:
  {export,import}       sub-command help
    export              export a collection
    import              export a collection

optional arguments:
  -h, --help            show this help message and exit
  --node NODE, -n NODE  node address
  --port PORT           TCP port where the node is listening on for API calls
  --user USER, -u USER  user name
  --password PASSWORD, -p PASSWORD
                        password, will be prompted if not given
  --token TOKEN, -t TOKEN
                        token key
  --scope SCOPE, -s SCOPE
                        set the initial scope
  --timeout TIMEOUT     connect and query timeout in seconds
  --ssl                 enable secure connection (SSL/TLS)
  --hide-connection-info
                        no address and port info in prompt
  --style {dracula,monokai,colorful,friendly,vim,none}
                        syntax highlighting style or none for disabled
  --version             print version and exit
```
### Help export

```
usage: things-prompt export [-h] [--structure-only] filename

positional arguments:
  filename          filename to store the export

optional arguments:
  -h, --help        show this help message and exit
  --structure-only  generates a textual export with only enumerators, types
                    and procedures; without this argument the export is not
                    readable but in MessagePack format and intented to be used
                    for import
```

### Help import

```
usage: things-prompt import [-h] [--tasks] filename

positional arguments:
  filename    filename to import

optional arguments:
  -h, --help  show this help message and exit
  --tasks     include tasks when importing a collection
```

## Special commands

command        | description
---------------|----------------------
`?`            | Show help.
`@scope`       | Switch to another scope, for example: `@:stuff`
`@scope query` | Run a single query in a given scope, for example `@n node_info();`
`CTRL + n`     | Insert a new line