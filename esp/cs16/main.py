#!/usr/bin/env python3
from pathlib import Path
from offsets import Offsets
import utils

process = next(Path("/mnt/name").glob("hl.exe-*"))

def get_local_team(base):
    memory = process / 'memory.vmem'
    with memory.open('rb', buffering=0) as f:
        f.seek(base)
        data = f.read(32)

    return data

def main():
    address = utils.get_client_base() + Offsets.PlayerTeam
    data = get_local_team(address)

    print(f'Address: 0x{address}')
    print(f'Bytes:   {data.hex(" ")}')

if __name__ == '__main__':
    main()
