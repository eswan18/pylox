import sys

from ._scan import scan
from ._parse import parse

class LoxError(Exception):
    def __init__(self, return_code: int):
        self.return_code = return_code

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
    try:
        run(contents)
    except LoxError as exc:
        sys.exit(exc.return_code)

def run_prompt():
    global had_error
    while True:
        try:
            line = input("> ")
        except EOFError:
            break

        try:
            run(line)
        except LoxError:
            continue

def run(source: str):
    tokens, scan_errors = scan(source)
    if scan_errors:
        for error in scan_errors:
            report(error)
        raise LoxError(65)
    print(tokens)

    ast, parse_errors = parse(tokens)
    if parse_errors:
        for error in parse_errors:
            report(error)
        raise LoxError(65)
    print(ast)

def report(exception):
    print(exception)
    #print(f"[line {exception.line_num}] Error: {exception.message}")

if __name__ == '__main__':
    main(sys.argv)
