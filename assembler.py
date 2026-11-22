#!/usr/bin/env python3
"""
Hack Assembler  --  Nand to Tetris capstone, Part B
K = 29   ->   K mod 3 = 2   ->   extra feature: print a warning if the same label
is written twice ("Warning: Line 6: label 'LOOP' is already defined ...").
The first definition is kept and the program is still assembled.

Usage:   python assembler.py Prog.asm [Prog.hack]
"""
import re
import sys
import os

# ----------------------------------------------------------------- tables
COMP = {
    # a = 0 (uses A)
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101', '!A': '0110001',
    '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
    'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
    # a = 1 (uses M)
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
    'D&M': '1000000', 'D|M': '1010101',
}
DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011',
        'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}

PREDEFINED = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
              'SCREEN': 16384, 'KBD': 24576}
PREDEFINED.update({f'R{i}': i for i in range(16)})

SYMBOL_RE = re.compile(r'^[A-Za-z_.$:][A-Za-z0-9_.$:]*$')
MAX_A_VALUE = 32767          # A-instruction has only 15 bits


# ----------------------------------------------------------------- helpers
def clean(line):
    """Remove comment and all whitespace."""
    return re.sub(r'\s+', '', line.split('//', 1)[0])


def to_bin16(value):
    return format(value, '016b')


def translate_c(text):
    """Translate dest=comp;jump.  Raises ValueError with a reason."""
    if text.count('=') > 1:
        raise ValueError("more than one '='")
    if text.count(';') > 1:
        raise ValueError("more than one ';'")

    dest, jump, rest = '', '', text
    if '=' in rest:
        dest, rest = rest.split('=', 1)
    if ';' in rest:
        rest, jump = rest.split(';', 1)
    comp = rest

    if comp == '':
        raise ValueError("missing computation part")
    if comp not in COMP:
        raise ValueError(f"unknown computation '{comp}'")
    if dest not in DEST:
        raise ValueError(f"unknown destination '{dest}'")
    if jump not in JUMP:
        raise ValueError(f"unknown jump '{jump}'")
    return '111' + COMP[comp] + DEST[dest] + JUMP[jump]


# ----------------------------------------------------------------- assembler
def assemble(lines):
    """Return (machine_code_list, error_list, warning_list)."""
    errors = []
    warnings = []
    label_lines = {}             # label name -> line where it was first defined
    symbols = dict(PREDEFINED)
    instructions = []            # (line_number, text)

    # ---------- first reading: strip comments/blank lines, record labels
    for lineno, raw in enumerate(lines, start=1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith('('):
            m = re.fullmatch(r'\(([^()]*)\)', text)
            if not m:
                errors.append(f"Line {lineno}: invalid instruction "
                              f"'{raw.strip()}' (bad label, expected (NAME))")
                continue
            name = m.group(1)
            if not SYMBOL_RE.match(name):
                errors.append(f"Line {lineno}: invalid instruction "
                              f"'{raw.strip()}' (illegal label name '{name}')")
            elif name in label_lines:                # same label written twice
                warnings.append(f"Warning: Line {lineno}: label '{name}' is "
                                f"already defined (first on line {label_lines[name]}); "
                                f"keeping the first one")
            elif name in symbols:
                errors.append(f"Line {lineno}: invalid instruction "
                              f"'{raw.strip()}' ('{name}' is a predefined symbol)")
            else:
                symbols[name] = len(instructions)   # ROM address of next instr
                label_lines[name] = lineno
            continue
        instructions.append((lineno, text))

    # ---------- second reading: translate to 16 bits
    next_var = 16
    output = []
    for lineno, text in instructions:
        if text.startswith('@'):
            sym = text[1:]
            if sym == '':
                errors.append(f"Line {lineno}: invalid instruction '@' "
                              f"(address missing after @)")
            elif sym.isdigit():
                value = int(sym)
                if value > MAX_A_VALUE:
                    errors.append(f"Line {lineno}: invalid instruction '{text}' "
                                  f"(value {value} is more than {MAX_A_VALUE})")
                else:
                    output.append(to_bin16(value))
            elif SYMBOL_RE.match(sym):
                if sym not in symbols:               # new variable
                    symbols[sym] = next_var
                    next_var += 1
                output.append(to_bin16(symbols[sym]))
            else:
                errors.append(f"Line {lineno}: invalid instruction '{text}' "
                              f"(illegal symbol '{sym}')")
        else:
            try:
                output.append(translate_c(text))
            except ValueError as e:
                errors.append(f"Line {lineno}: invalid instruction '{text}' ({e})")
    return output, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py Prog.asm [Prog.hack]")
        return 2
    src = sys.argv[1]
    if not src.lower().endswith('.asm'):
        print(f"Error: '{src}' is not an .asm file")
        return 2
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.hack'

    try:
        with open(src, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"Error: cannot read '{src}': {e.strerror}")
        return 2

    code, errors, warnings = assemble(lines)
    for w in warnings:
        print(w)
    if errors:
        errors.sort(key=lambda m: int(re.match(r'Line (\d+):', m).group(1)))
        for msg in errors:
            print(msg)
        print(f"Assembly failed: {len(errors)} error(s). No output file written.")
        return 1

    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(code) + '\n')
    note = f", {len(warnings)} warning(s)" if warnings else ""
    print(f"OK: {src} -> {dst} ({len(code)} instructions{note})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
