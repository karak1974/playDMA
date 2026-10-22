#!/usr/bin/env python3
from pathlib import Path
from offsets import Offsets
import utils
import struct

process = utils.process

def get_local_team(address):
    memory = process / "memory.vmem"

    with memory.open("rb", buffering=0) as f:
        f.seek(address)
        data = f.read(4)

    if len(data) != 4:
        raise RuntimeError("Could not read 4 bytes")

    return struct.unpack("<I", data)[0]

def debug_team_address(address):
    memory = process / "memory.vmem"

    with memory.open("rb", buffering=0) as f:
        for offset in (-16, 0, 16):
            current = address + offset
            f.seek(current)
            data = f.read(16)

            print(f"0x{current:X}: {data.hex(' ')}")

def main():
    client_base = utils.get_client_base()
    engine_base = utils.get_engine_base()

    address = client_base + Offsets.WeaponID
    local_team = get_local_team(address)

    print(f"Client base: 0x{client_base:X}")
    print(f"Engine base: 0x{engine_base:X}")
    print(f"Team address: 0x{address:X}")
    print(f"Local team: {local_team}")

    debug_team_address(address)

if __name__ == "__main__":
    main()

