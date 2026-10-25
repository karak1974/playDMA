#!/usr/bin/env python3
import struct
import memprocfs
from offsets import Offsets

def read(process, address, fmt):
    size = struct.calcsize(fmt)
    data = process.memory.read(address, size, memprocfs.FLAG_NOCACHE)

    if len(data) != size:
        raise RuntimeError(f"Read failed at 0x{address:X}")

    return struct.unpack(fmt, data)[0]

def mapped(mappings, address, size=1):
    return any(
        m["va"] <= address
        and address + size <= m["va"] + m["size"]
        for m in mappings
    )

def main():
    vmm = memprocfs.Vmm(["-device", "fpga", "-memmap", "auto"])

    try:
        process = vmm.process("cstrike_win64.exe")
        client_base = process.module("client.dll").base
        mappings = process.maps.pte()

        # Local player pointer
        pointer_address = client_base + Offsets.LocalPlayer

        if not mapped(mappings, pointer_address, 8):
            raise RuntimeError("Player pointer address not mapped")

        player = read(process, pointer_address, "<Q")

        if not mapped(mappings, player):
            raise RuntimeError("Invalid player pointer")

        print(f"PID:         {process.pid}")
        print(f"Client base: 0x{client_base:X}")
        print(f"Player:      0x{player:X}")

        # Player values
        fields = {
            "Health": (Offsets.M_iHealth, "<i"),
        }

        for name, (offset, fmt) in fields.items():
            address = player + offset
            size = struct.calcsize(fmt)

            if not mapped(mappings, address, size):
                print(f"{name}: unavailable")
                continue

            value = read(process, address, fmt)
            print(f"{name}: {value}")

    finally:
        vmm.close()


if __name__ == "__main__":
    main()
