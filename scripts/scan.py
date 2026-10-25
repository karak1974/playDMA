#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

PTE = re.compile(
    r'^\s*[0-9a-fA-F]+\s+\d+\s+[0-9a-fA-F]+\s+'
    r'([0-9a-fA-F]+)-([0-9a-fA-F]+)\s+([-rwx]+)(?:\s+(.*))?$'
)

def hex_regex(value, max_star=256, allow_star=False):
    parts = []
    maximum = 0
    for token in value.split():
        if token == '??':
            parts.append(b'.')
            maximum += 1
        elif token == '*' and allow_star:
            parts.append(rb'.{1,' + str(max_star).encode() + rb'}?')
            maximum += max_star
        elif re.fullmatch(r'[0-9a-fA-F]{2}', token):
            parts.append(re.escape(bytes.fromhex(token)))
            maximum += 1
        else:
            raise ValueError(f'Invalid token: {token!r} (use hex, ??, or * in --pattern)')
    return b''.join(parts), maximum

def regions(path, executable, scope):
    for line in path.read_text(errors='replace').splitlines():
        match = PTE.match(line)
        if not match:
            continue
        first, last, permissions, name = match.groups()
        name = (name or '').strip()
        image = name.lower() == executable.lower()
        writable = 'w' in permissions
        if 'r' in permissions and (
            (scope == 'image' and image) or
            (scope == 'writable' and writable) or
            (scope == 'both' and (image or writable))
        ):
            yield int(first, 16), int(last, 16) + 1, name

def scan(process, prefix, target, suffix, scope, max_star):
    if not target.strip():
        raise ValueError('--pattern cannot be empty')
    if '*' in target.split() and not suffix.strip():
        raise ValueError('Use --suffix with * so the scanner knows where to stop')

    prefix_re, prefix_max = hex_regex(prefix)
    target_re, target_max = hex_regex(target, max_star, allow_star=True)
    suffix_re, suffix_max = hex_regex(suffix)
    regex = re.compile(prefix_re + b'(' + target_re + b')' + suffix_re, re.DOTALL)
    overlap = prefix_max + target_max + suffix_max - 1

    executable = process.name.rsplit('-', 1)[0]
    memory = process / 'memory.vmem'
    count = 0

    with memory.open('rb', buffering=0) as source:
        for start, end, name in regions(process / 'memmap/pte.txt', executable, scope):
            previous = b''
            position = start
            while position < end:
                source.seek(position)
                block = source.read(min(1024 * 1024, end - position))
                if not block:
                    break

                data = previous + block
                base = position - len(previous)
                for match in regex.finditer(data):
                    if base + match.end() <= position:
                        continue  # Match was already reported
                    address = base + match.start(1)
                    target_bytes = match.group(1)
                    print(f'0x{address:X} ({name or "unnamed"}) {target_bytes.hex(" ")}')
                    count += 1

                previous = data[-overlap:] if overlap > 0 else b''
                position += len(block)

    print(f'Matches: {count}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('process_dir', type=Path)
    parser.add_argument('--pattern', required=True, help='Hex bytes, ?? (one byte), * (variable length)')
    parser.add_argument('--prefix', default='')
    parser.add_argument('--suffix', default='')
    parser.add_argument('--scope', choices=('writable', 'image', 'both'), default='writable')
    parser.add_argument('--max-star', type=int, default=256, help='Maximum bytes per * (default: 256)')
    args = parser.parse_args()

    if not 1 <= args.max_star <= 65536:
        parser.error('--max-star must be between 1 and 65536')
    try:
        scan(args.process_dir, args.prefix, args.pattern, args.suffix, args.scope, args.max_star)
    except ValueError as exc:
        parser.error(str(exc))

if __name__ == '__main__':
    main()
