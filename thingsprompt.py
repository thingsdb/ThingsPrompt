#!/usr/bin/env python
'''ThingsPrompt

Shell client for ThingsDB
'''
import os
import sys
import argparse
import asyncio
import getpass
import re
import json
import base64
import ssl
import functools
from setproctitle import setproctitle
from thingsdb.client import Client
from thingsdb.exceptions import ThingsDBError
from prompt_toolkit import __version__ as ptk_version
from prompt_toolkit.filters import Condition
from prompt_toolkit.history import FileHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name
from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import Comment, Keyword, Name, Number, String, Text, \
    Operator, Punctuation, Whitespace


__version__ = '1.0.6'  # keep equal to the one in setup.py


class ThingsDBLexer(RegexLexer):
    """
    Lexer for the ThingsDB programming language.

    .. versionadded:: 2.9
    """
    name = 'ThingsDB'
    aliases = ['ti', 'thingsdb']
    filenames = ['*.ti']

    tokens = {
        'root': [
            include('expression'),
        ],
        'expression': [
            include('comments'),
            include('whitespace'),

            # numbers
            (r'[-+]?0b[01]+', Number.Bin),
            (r'[-+]?0o[0-8]+', Number.Oct),
            (r'([-+]?0x[0-9a-fA-F]+)', Number.Hex),
            (r'[-+]?[0-9]+', Number.Integer),
            (r'[-+]?((inf|nan)([^0-9A-Za-z_]|$)|[0-9]*\.[0-9]+(e[+-][0-9]+)?)',
             Number.Float),

            # strings
            (r'(?:"(?:[^"]*)")+', String.Double),
            (r"(?:'(?:[^']*)')+", String.Single),
            (r"(?:`(?:[^`]*)`)+", String.Backtick),

            # literals
            (r'(true|false|nil)\b', Keyword.Constant),

            # name constants
            (r'(FULL|USER|GRANT|CHANGE|JOIN|RUN|QUERY|'
             r'DEBUG|INFO|WARNING|ERROR|CRITICAL|'
             r'NO_IDS|INT_MIN|INT_MAX|MATH_E|MATH_PI)\b', Name.Constant),

            # regular expressions
            (r'(/[^/\\]*(?:\\.[^/\\]*)*/i?)', String.Regex),

            # name, assignments and functions
            include('names'),

            (r'[(){}\[\],;]', Punctuation),
            (r'[+\-*/%&|<>^!~@=:?]', Operator),
        ],
        'names': [
            (r'(\.)'
             r'(first|last|then|else|load|at|again_in|again_at|err|cancel|'
             r'closure|set_closure|args|set_args|owner|set_owner|equals|copy|'
             r'dup|assign|week|weekday|yday|zone|len|call|doc|emit|extract|'
             r'choice|code|format|msg|each|every|extend|extend_unique|filter|'
             r'find|flat|find_index|has|index_of|count|sum|is_unique|unique|'
             r'join|map|map_id|map_wrap|map_type|vmap|move|pop|push|fill|'
             r'remove|replace|restrict|restriction|shift|sort|splice|to|add|'
             r'one|clear|contains|ends_with|name|lower|replace|reverse|'
             r'starts_with|split|test|trim|trim_left|trim_right|upper|del|ren|'
             r'to_type|to_thing|get|id|keys|reduce|set|some|value|values|wrap|'
             r'unshift|unwrap|search)'
             r'(\()',
             bygroups(Name.Function, Name.Function, Punctuation), 'arguments'),
            (r'(alt_raise|assert|base64_encode|base64_decode|bool|bytes|'
             r'closure|datetime|deep|future|is_future|del_enum|del_type|room|'
             r'is_room|task|tasks|is_task|is_email|is_url|is_tel|is_time_zone|'
             r'timeit|enum|enum_info|enum_map|enums_info|err|regex|is_regex|'
             r'change_id|float|has_enum|has_type|int|is_array|is_ascii|'
             r'is_float|is_bool|is_bytes|is_closure|is_datetime|is_enum|'
             r'is_err|is_mpdata|is_inf|is_int|is_list|is_nan|is_nil|is_raw|'
             r'is_set|is_str|is_thing|is_timeval|is_tuple|is_utf8|json_dump|'
             r'json_load|list|log|import|export|root|mod_enum|mod_type|new|'
             r'new_type|now|raise|rand|range|randint|randstr|refs|rename_enum|'
             r'set|set_enum|set_type|str|thing|timeval|try|type|type_assert|'
             r'type_count|type_info|types_info|nse|wse|backup_info|'
             r'backups_info|backups_ok|counters|del_backup|has_backup|'
             r'new_backup|node_info|nodes_info|reset_counters|restart_module|'
             r'set_log_level|shutdown|has_module|del_module|module_info|'
             r'modules_info|new_module|deploy_module|rename_module|'
             r'refresh_module|set_module_conf|set_module_scope|'
             r'collections_info|del_collection|del_expired|del_node|del_token|'
             r'del_user|grant|has_collection|has_node|has_token|has_user|'
             r'new_collection|new_node|new_token|new_user|rename_collection|'
             r'rename_user|restore|revoke|set_password|set_time_zone|'
             r'set_default_deep|time_zones_info|user_info|users_info|'
             r'del_procedure|has_procedure|new_procedure|mod_procedure|'
             r'procedure_doc|procedure_info|procedures_info|rename_procedure|'
             r'run|assert_err|auth_err|bad_data_err|cancelled_err|'
             r'rename_type|forbidden_err|lookup_err|max_quota_err|node_err|'
             r'num_arguments_err|operation_err|overflow_err|syntax_err|'
             r'collection_info|type_err|value_err|zero_div_err|abs|ceil|cos|'
             r'exp|floor|log10|log2|loge|pow|round|sin|sqrt|tan)'
             r'(\()',
             bygroups(Name.Function, Punctuation),
             'arguments'),
            (r'(\.[A-Za-z_][0-9A-Za-z_]*)'
             r'(\s*)(=)',
             bygroups(Name.Attribute, Text, Operator)),
            (r'\.[A-Za-z_][0-9A-Za-z_]*', Name.Attribute),
            (r'([A-Za-z_][0-9A-Za-z_]*)(\s*)(=)',
             bygroups(Name.Variable, Text, Operator)),
            (r'[A-Za-z_][0-9A-Za-z_]*', Name.Variable),
        ],
        'whitespace': [
            (r'\n', Whitespace),
            (r'\s+', Whitespace),
        ],
        'comments': [
            (r'//(.*?)(\n|$)', Comment.Single),
            (r'/\*', Comment.Multiline, 'comment'),
        ],
        'comment': [
            (r'[^*/]+', Comment.Multiline),
            (r'/\*', Comment.Multiline, '#push'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[*/]', Comment.Multiline),
        ],
        'arguments': [
            include('expression'),
            (',', Punctuation),
            (r'\(', Punctuation, '#push'),
            (r'\)', Punctuation, '#pop'),
        ]
    }


PTK3 = ptk_version.startswith('3.')
USE_FUN = re.compile(r'^\s*(@\s?[\:\/0-9a-zA-Z_]+)\s*$')
SCOPE_QUERY = re.compile(r'^\s*(@[\:0-9a-zA-Z_]+)\s+(.*)$')
SCOPE_RE = re.compile(
    r'^(@([a-z]*):([a-zA-Z_][a-zA-Z0-9_]*))'
    r'|(/([a-z]*)/([a-zA-Z_][a-zA-Z0-9_]*))$')

TAB = ' ' * 4
HELP = f'''
Version:
    {__version__}

Special commands:

?
    This help.
<@scope>
    Switch to another scope
<@scope> <query>
    Run a single query in a given scope
CTRL + n
    Insert a new line
'''

bindings = KeyBindings()
session = None


def collection_from_scope(scope: str):
    m = SCOPE_RE.match(scope)
    if m is None:
        return
    if m.group(1) is not None:
        return m.group(3) if 'collection'.startswith(m.group(2)) else None
    if m.group(4) is not None:
        return m.group(6) if 'collection'.startswith(m.group(5)) else None
    return None


class BinEncode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode("utf-8")
        return json.JSONEncoder.default(self, obj)


@Condition
def is_active():
    return session.multiline


def on_enter_new_line(event):
    last_enter_idx = event.app.current_buffer.text.rfind('\n')
    last_line = event.app.current_buffer.text[last_enter_idx+1:].rstrip()

    idx = 0
    for idx, c in enumerate(last_line):
        if not c.isspace():
            break

    indent = last_line[:idx]

    if last_line and last_line[-1] in ('{', '(', '['):
        indent += TAB

    event.app.current_buffer.insert_text('\n' + indent)


@bindings.add('tab')
def _(event):
    """Insert TAB"""
    event.app.current_buffer.insert_text(TAB)


@bindings.add('c-n')
def _(event):
    on_enter_new_line(event)


@bindings.add('backspace')
def _(event):
    buffer = event.app.current_buffer
    text = buffer.text[:buffer.cursor_position]
    indent = len(text) - len(text.rstrip(' '))
    if indent and indent % 4 == 0:
        for _ in range(4):
            buffer.delete_before_cursor()
    else:
        buffer.delete_before_cursor()


async def connect(client, args, auth):
    await client.connect(args.node, args.port, timeout=args.timeout)
    await client.authenticate(*auth, timeout=args.timeout)


def set_prompt(client, session, hide_connection_info):
    scope = client.get_default_scope()
    if hide_connection_info:
        title = f'({scope})'
    else:
        title = f'{client.connection_info()} ({scope})'
    session.message = f'{title}> '


async def prompt_loop(client, args):
    global session
    try:
        history_file = os.path.join(
            os.path.expanduser('~'),
            '.config',
            'ThingsPrompt',
            'history'
        )
        if not os.path.exists(history_file):
            path = os.path.dirname(history_file)
            if not os.path.exists(path):
                os.mkdir(path, 0o700)
            open(history_file, 'w').close()
            os.chmod(history_file, 0o600)

        history = FileHistory(history_file)
    except Exception:
        history = InMemoryHistory()

    if args.style == 'none':
        session = PromptSession(history=history)
    else:
        style = style_from_pygments_cls(get_style_by_name(args.style))
        session = PromptSession(
            history=history,
            lexer=PygmentsLexer(ThingsDBLexer),
            style=style)
    session.client = client

    if PTK3:
        aprompt = functools.partial(
            session.prompt_async,
            key_bindings=bindings)
    else:
        aprompt = functools.partial(
            session.prompt,
            async_=True,
            key_bindings=bindings)

    set_prompt(client, session, args.hide_connection_info)

    while True:
        try:
            query = await aprompt()

            if query is None:
                continue

            if query.strip() == '?':
                print(HELP)
                continue

            use = USE_FUN.match(query)
            if use:
                scope = use.group(1)
                scope = scope.strip('\'"')
                if scope[1] == ' ':
                    scope = scope[2:]

                client.set_default_scope(scope)
                set_prompt(client, session, args.hide_connection_info)
                continue

            scope = SCOPE_QUERY.match(query)
            if scope:
                query = scope.group(2)
                scope = scope.group(1)
            else:
                scope = None

            if not client.is_connected():
                print('not connected')
                continue

            try:
                res = await client.query(
                    query,
                    scope=scope,
                    timeout=args.timeout)
            except ThingsDBError as e:
                print(f'{e.__class__.__name__}: {e}')
            else:
                print(json.dumps(res, sort_keys=True, indent=4, cls=BinEncode))

        except (EOFError, KeyboardInterrupt):
            return


async def do_export(client, fn: str, collection: str, dump: bool):
    with open(fn, 'wb') as f:
        try:
            dump = await client.query("""//ti
                export({dump:,});
            """, dump=dump, scope=f'//{collection}')
        except ThingsDBError as e:
            print(f'{e.__class__.__name__}: {e}')
        f.write(dump)


async def do_import(client, fn: str, collection: str, import_tasks: bool):
    with open(fn, 'rb') as f:
        data = f.read()
        has_collection = await client.has_collection(collection)
        try:
            if has_collection is False:
                await client.new_collection(collection)

            await client.query("""//ti
                import(data, {import_tasks:,});
            """, data=data, import_tasks=import_tasks, scope=f'//{collection}')
        except ThingsDBError as e:
            print(f'{e.__class__.__name__}: {e}')


def main():
    setproctitle('things-prompt')

    if not PTK3:
        from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
        use_asyncio_event_loop()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--node', '-n',
        type=str,
        default='localhost',
        help='node address')

    parser.add_argument(
        '--port',
        type=int,
        default=9200,
        help='TCP port where the node is listening on for API calls')

    parser.add_argument(
        '--user', '-u',
        type=str,
        help='user name')

    parser.add_argument(
        '--password', '-p',
        type=str,
        help='password, will be prompted if not given')

    parser.add_argument(
        '--token', '-t',
        type=str,
        help='token key')

    parser.add_argument(
        '--scope', '-s',
        type=str,
        default='@thingsdb',
        help='set the initial scope')

    parser.add_argument(
        '--timeout',
        type=int,
        help='connect and query timeout in seconds')

    parser.add_argument(
        '--ssl',
        action='store_true',
        help='enable secure connection (SSL/TLS)')

    parser.add_argument(
        '--hide-connection-info',
        action='store_true',
        help='no address and port info in prompt')

    parser.add_argument(
        '--style',
        default='dracula',
        choices=['dracula', 'monokai', 'colorful', 'friendly', 'vim', 'none'],
        help='syntax highlighting style or none for disabled')

    parser.add_argument(
        '--version',
        action='store_true',
        help='print version and exit')

    subparsers = parser.add_subparsers(help='sub-command help')
    parser_exp = subparsers.add_parser(
        'export',
        help='export a collection')

    parser_exp.add_argument(
        'filename',
        help='filename to store the export')

    parser_exp.add_argument(
        '--structure-only',
        action='store_true',
        help=(
            'generates a textual export with only enumerators, types and '
            'procedures; '
            'without this argument the export is not readable but in '
            'MessagePack format and intented to be used for import'))

    parser_imp = subparsers.add_parser(
        'import',
        help='export a collection')

    parser_imp.add_argument(
        'filename',
        help='filename to import')

    parser_imp.add_argument(
        '--tasks',
        action='store_true',
        help='include tasks when importing a collection')

    args = parser.parse_args()

    if args.version:
        sys.exit(__version__)

    if args.token is None:
        if args.user is None:
            sys.exit(
                'one of the arguments -t/--token or -u/--user is required')

        if args.password is None:
            args.password = getpass.getpass('password: ')

        auth = [args.user, args.password]
    else:
        if args.user is not None:
            sys.exit('use arguments -t/--token or -u/--user, not both')
        auth = [args.token]

    if args.ssl:
        context = ssl.SSLContext( ssl.PROTOCOL_TLS_CLIENT )
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        client = Client(ssl=context)
    else:
        client = Client(ssl=None)

    client.set_default_scope(args.scope)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(connect(client, args, auth))
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}', file=sys.stderr)
        exit(1)

    has_import = hasattr(args, 'tasks')
    has_export = hasattr(args, 'structure_only')

    if has_export:
        collection = collection_from_scope(args.scope)
        if collection is None:
            sys.exit(
                'not a valid collection scope; '
                'use --scope and provide a collection scope (e.g //stuff)')
        dump = not args.structure_only
        fn = args.filename
        loop.run_until_complete(do_export(client, fn, collection, dump))
    elif has_import:
        if not args.scope:
            sys.exit('argument --import requires a scope (--scope)')
        collection = collection_from_scope(args.scope)
        if collection is None:
            sys.exit('not a valid collection scope')
        fn = args.filename
        loop.run_until_complete(do_import(client, fn, collection, args.tasks))
    else:
        with patch_stdout():
            loop.run_until_complete(prompt_loop(client, args))

    client.close()
    loop.run_until_complete(client.wait_closed())


if __name__ == '__main__':
    main()
