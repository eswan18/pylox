import sys

from ._scan import scan
from ._parse import Parser
from ._interpret import Interpreter
from ._errors import LoxError


def main(args: list[str]):
    if len(args) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(args) == 2:
        run_file(args[1])
    else:
        run_prompt()


def run_file(filename: str):
    with open(filename, 'rt') as f:
        contents = f.read()
    interpreter = Interpreter()
    try:
        run(contents, interpreter)
    except LoxError as exc:
        sys.exit(exc.return_code)


def run_prompt():
    global had_error
    interpreter = Interpreter()
    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        try:
            run(line, interpreter)
        except LoxError:
            continue


def run(source: str, interpreter: Interpreter):
    tokens, scan_errors = scan(source)
    if scan_errors:
        for scan_error in scan_errors:
            report(scan_error)
        raise LoxError(65)

    parser = Parser()
    statements = parser.parse(tokens)
    if len(parser.errors) >= 1:
        for parse_error in parser.errors:
            report(parse_error)
        raise LoxError(65)

    runtime_error = interpreter.interpret(statements)
    if runtime_error is not None:
        report(runtime_error)
        raise LoxError(70)


def report(exception):
    print(exception)


if __name__ == '__main__':
    main(sys.argv)
