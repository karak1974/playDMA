#!/usr/bin/env python3
"""Read a CS 1.6 team value through MemProcFS; report unmapped pages."""
from pathlib import Path
from offsets import Offsets

matches = list(Path('/mnt/name').glob('hl.exe-*'))
if len(matches) != 1:
    raise SystemExit(f'Expected one hl.exe process, found {len(matches)}')
process = matches[0]

client_base = int((process / 'modules/client.dll/base.txt').read_text().strip(), 16)
engine_base = int((process / 'modules/hw.dll/base.txt').read_text().strip(), 16)
team_address = client_base + Offsets.PlayerTeam

print(f'Process:     {process.name}')
print(f'Client base: 0x{client_base:X}')
print(f'Engine base: 0x{engine_base:X}')
print(f'Team addr:   0x{team_address:X}')

mapped = False
for line in (process / 'memmap/pte.txt').read_text().splitlines():
    fields = line.split()
    if len(fields) < 4 or '-' not in fields[3]:
        continue
    first, last = fields[3].split('-', 1)
    try:
        if int(first, 16) <= team_address <= int(last, 16):
            mapped = True
            break
    except ValueError:
        continue

if not mapped:
    print('Local team:  unavailable (not present in PTE map; zero is not trustworthy)')
else:
    with (process / 'memory.vmem').open('rb', buffering=0) as memory:
        memory.seek(team_address)
        raw = memory.read(4)
    if len(raw) != 4:
        print(f'Local team:  read failed ({len(raw)} of 4 bytes)')
    else:
        print(f'Raw bytes:   {raw.hex(" ")}')
        print(f'Local team:  {int.from_bytes(raw, "little")}')
