class Offsets:
    # client.dll
    LocalPlayer = 0x5F4B98
    EntityList = 0x6098F8 # List of players
    Entity_loop_distance = 0x10 # Distance between each player data structure
    ForceAttack = 0x676DF0
    ForceJump = 0x676DE0

    # engine.dll
    M_angRotation = 0x53F4E4
    M_iNumPlayers = 0x6DB960

    # CBasePlayer
    M_iHealth = 0xD0
    M_iTeamNum = 0xD8
    M_vecOrigin = 0x320
    M_fFlags = 0x440
    M_iCrosshairId = 0x1B20 # 0 = nothing, 1-64 target
    M_flFlashMaxAlpha = 0x1A54
