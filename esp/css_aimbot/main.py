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
        engine_base = process.module("engine.dll").base
        mappings = process.maps.pte()

        client_pointer_address = client_base + Offsets.LocalPlayer
        engine_pointer_address = engine_base

        if not mapped(mappings, client_pointer_address, 8):
            raise RuntimeError("Player pointer address not mapped")

        player = read(process, client_pointer_address, "<Q")

        if not mapped(mappings, player):
            raise RuntimeError("Invalid player pointer")

        print(f"PID: {process.pid}")
        print(f"Client base: 0x{client_base:X}")
        print(f"Player base: 0x{player:X}")

        fields = {
            "Health": (player, Offsets.M_iHealth, "<i"),
            "TeamNum": (player, Offsets.M_iTeamNum, "<i"),
            "CrosshairID": (player, Offsets.M_iCrosshairId, "<i"),
            "NumPlayers": (engine_base, Offsets.M_iNumPlayers, "<I"),
        }

        for name, (base, offset, fmt) in fields.items():
            address = base + offset
            size = struct.calcsize(fmt)

            if not mapped(mappings, address, size):
                print(f"{name}: unavailable")
                continue

            value = read(process, address, fmt)
            print(f"{name}: {value}")
            if name == "TeamNum":
                print(f"Team: {Offsets.get_team(int(value))}")

    finally:
        vmm.close()


if __name__ == "__main__":
    main()
