import sys

from .scan import get_tokens

had_error = False

def main(args: list[str]):
    if len(args) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(args) == 2:
        run_file(args[0])
    else:
        run_prompt()

def run_file(filename: str):
    with open(filename, 'rt') as f:
        contents = f.read()
    run(contents)
    if had_error:
        sys.exit(65)

def run_prompt():
    global had_error
    while True:
        line = input("> ")
        run(line)
        had_error = False

def run(source: str):
    tokens = get_tokens(source)
    # For now, just print the tokens.
    for token in tokens:
        print(token)

def error(line_num: int, message: str):
    report(line_num, '', message)

def report(line_num: int, where: str, message: str):
    global had_error
    print(f"[line {line_num}] Error {where}: {message}")
    had_error = True

if __name__ == '__main__':
    main(sys.argv)
