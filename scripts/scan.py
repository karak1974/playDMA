#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

PTE = re.compile(r'^\s*[0-9a-fA-F]+\s+\d+\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)\s+([-rwx]+)(?:\s+(.*))?$')

def hex_regex(value):
    tokens = value.split()
    if any(not re.fullmatch(r'[0-9a-fA-F]{2}|\?\?', t) for t in tokens):
        raise ValueError('Patterns must contain hex bytes or ?? separated by spaces')
    return b''.join(b'.' if t == '??' else re.escape(bytes.fromhex(t)) for t in tokens), len(tokens)

def regions(path, executable, scope):
    for line in path.read_text(errors='replace').splitlines():
        match = PTE.match(line)
        if not match:
            continue
        first, last, permissions, name = match.groups()
        name = (name or '').strip()
        image = name.lower() == executable.lower()
        writable = 'w' in permissions
        if 'r' in permissions and (scope == 'both' and (image or writable) or
                                   scope == 'image' and image or
                                   scope == 'writable' and writable):
            yield int(first, 16), int(last, 16) + 1, name

def scan(process, prefix, target, suffix, scope):
    prefix_re, prefix_len = hex_regex(prefix)
    target_re, target_len = hex_regex(target)
    suffix_re, suffix_len = hex_regex(suffix)
    if not target_len:
        raise ValueError('--pattern cannot be empty')
    total = prefix_len + target_len + suffix_len
    regex = re.compile(prefix_re + b'(' + target_re + b')' + suffix_re, re.DOTALL)
    executable = process.name.rsplit('-', 1)[0]
    pte = process / 'memmap' / 'pte.txt'
    memory = process / 'memory.vmem'

    with memory.open('rb', buffering=0) as source:
        for start, end, name in regions(pte, executable, scope):
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
                    whole_end = base + match.end()
                    if whole_end <= position:  # Already reported in previous chunk
                        continue
                    target_address = base + match.start(1)
                    target_bytes = match.group(1)
                    print(f'0x{target_address:X} ({name or "unnamed"}) {target_bytes.hex(" ")}')

                previous = data[-(total - 1):] if total > 1 else b''
                position += len(block)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('process_dir', type=Path)
    parser.add_argument('--pattern', required=True, help='Target hex bytes; ?? is any byte')
    parser.add_argument('--prefix', default='', help='Optional preceding hex pattern')
    parser.add_argument('--suffix', default='', help='Optional following hex pattern')
    parser.add_argument('--scope', choices=('writable', 'image', 'both'), default='writable')
    args = parser.parse_args()
    try:
        scan(args.process_dir, args.prefix, args.pattern, args.suffix, args.scope)
    except ValueError as exc:
        parser.error(str(exc))

if __name__ == '__main__':
    main()

