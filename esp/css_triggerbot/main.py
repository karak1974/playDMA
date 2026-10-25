#!/usr/bin/env python3
import time
import struct
import memprocfs
from offsets import Offsets

def read_memory(process, mappings, address, fmt):
    size = struct.calcsize(fmt)

    if not mapped(mappings, address, size):
        return None

    try:
        data = process.memory.read(
            address, size, memprocfs.FLAG_NOCACHE
        )

        if len(data) != size:
            return None

        return struct.unpack(fmt, data)[0]

    except (RuntimeError, OSError):
        return None

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

        while True:
            player = read_memory(
                process, mappings,
                client_base + Offsets.LocalPlayer, "<Q"
            )

            print("\033[H\033[J", end="")

            print(f"PID:         {process.pid}")
            print(f"Client base: 0x{client_base:X}")
            print(f"Player:      {hex(player) if player else 'unavailable'}")
            print()

            if not player or not mapped(mappings, player):
                print("Player unavailable")
                time.sleep(0.5)
                continue

            fields = {
                "Health":      (player, Offsets.M_iHealth, "<i"),
                "TeamNum":     (player, Offsets.M_iTeamNum, "<i"),
                "CrosshairID": (player, Offsets.M_iCrosshairId, "<i"),
                "NumPlayers":  (engine_base, Offsets.M_iNumPlayers, "<I"),
            }

            values = {}

            for name, (base, offset, fmt) in fields.items():
                value = read_memory(
                    process, mappings, base + offset, fmt
                )

                values[name] = value
                print(f"{name}: {value if value is not None else 'unavailable'}")

            crosshair_id = values["CrosshairID"]

            if crosshair_id is not None and crosshair_id > 0:
                entity_address = (
                    client_base
                    + Offsets.EntityList
                    + (crosshair_id - 1) * Offsets.Entity_loop_distance
                )

                target_entity = read_memory(
                    process, mappings, entity_address, "<Q"
                )

                if target_entity:
                    target_team = read_memory(
                        process, mappings,
                        target_entity + Offsets.M_iTeamNum, "<I"
                    )

                    player_team = read_memory(
                        process, mappings,
                        player + Offsets.M_iTeamNum, "<I"
                    )

                    print(f"Target team: {target_team}")
                    print(f"Player team: {player_team}")

                    if target_team is not None and player_team is not None:
                        if target_team != player_team:
                            print("ATTACK")

                else:
                    print("Target entity: unavailable")
            else:
                print("Target entity: none")

            time.sleep(0.5)
    finally:
        vmm.close()


if __name__ == "__main__":
    main()

# DEVNOTE TODO
# If new game(not round) starts we have to find the playr entity again