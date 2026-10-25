#!/usr/bin/env python3
import time
import struct
import memprocfs
from offsets import Offsets

ATTACK_PRESS = 5
ATTACK_RELEASE = 4

def mapped(mappings, address, size=1):
    return any(
        m["va"] <= address
        and address + size <= m["va"] + m["size"]
        for m in mappings
    )

def read_memory(process, mappings, address, fmt="<I"):
    size = struct.calcsize(fmt)

    if not mapped(mappings, address, size):
        return None

    try:
        data = process.memory.read(address, size, memprocfs.FLAG_NOCACHE)
        return struct.unpack(fmt, data)[0] if len(data) == size else None
    except (RuntimeError, OSError):
        return None

def write_memory(process, mappings, address, value):
    if not mapped(mappings, address, 4):
        raise RuntimeError(f"Unmapped address: 0x{address:X}")

    process.memory.write(address, struct.pack("<I", value))

def main():
    vmm = memprocfs.Vmm(["-device", "fpga", "-memmap", "auto"])

    try:
        process = vmm.process("cstrike_win64.exe")
        client_base = process.module("client.dll").base
        engine_base = process.module("engine.dll").base
        mappings = process.maps.pte()

        player_address = client_base + Offsets.LocalPlayer
        attack_address = client_base + Offsets.ForceAttack

        while True:
            player = read_memory(process, mappings, player_address, "<Q")

            if not player or not mapped(mappings, player):
                mappings = process.maps.pte()
                time.sleep(0.1)
                continue

            fields = {
                "Health": (player, Offsets.M_iHealth, "<i"),
                "TeamNum": (player, Offsets.M_iTeamNum, "<I"),
                "CrosshairID": (player, Offsets.M_iCrosshairId, "<i"),
                "NumPlayers": (engine_base, Offsets.M_iNumPlayers, "<I"),
            }

            values = {
                name: read_memory(process, mappings, base + offset, fmt)
                for name, (base, offset, fmt) in fields.items()
            }

            player_team = values["TeamNum"]
            crosshair_id = values["CrosshairID"]

            target_entity = None
            target_team = None

            if player_team in (2, 3) and crosshair_id is not None and 1 <= crosshair_id <= 64:
                entity_address = (
                    client_base
                    + Offsets.EntityList
                    + (crosshair_id - 1) * Offsets.Entity_loop_distance
                )

                target_entity = read_memory(process, mappings, entity_address, "<Q")

                if target_entity and target_entity != player:
                    target_team = read_memory(process, mappings, target_entity + Offsets.M_iTeamNum)

                    # Only attack enemies
                    if target_team in (2, 3) and player_team != target_team:

                        # Recheck just before attacking
                        if read_memory(process, mappings, attack_address) == ATTACK_RELEASE:
                            try:
                                write_memory(process, mappings, attack_address, ATTACK_PRESS)
                                time.sleep(0.05)
                            finally:
                                write_memory(process, mappings, attack_address, ATTACK_RELEASE)

            print("\033[H\033[J", end="")
            print(f"PID:           {process.pid}")
            print(f"Client base:   0x{client_base:X}")
            print(f"Player:        0x{player:X}")
            print()

            for name, value in values.items():
                print(f"{name}: {value}")

            print(f"Target entity: {hex(target_entity) if target_entity else 'None'}")
            print(f"Target team:   {target_team}")
            print(f"Enemy:         {player_team in (2, 3) and target_team in (2, 3) and player_team != target_team}")

            time.sleep(0.1)

    finally:
        vmm.close()


if __name__ == "__main__":
    main()

# DEVNOTE TODO
# If new game(not round) starts we have to find the playr entity again