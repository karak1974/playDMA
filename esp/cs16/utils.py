from pathlib import Path

process = next(Path("/mnt/name").glob("hl.exe-*"))

def get_client_base():
    module = "client.dll"
    base_file = process / "modules" / module / "base.txt"
    base = int(base_file.read_text().strip(), 16)

    return base

def get_hw_base():
    module = "hw.dll"
    base_file = process / "modules" / module / "base.txt"
    base = int(base_file.read_text().strip(), 16)

    return base

