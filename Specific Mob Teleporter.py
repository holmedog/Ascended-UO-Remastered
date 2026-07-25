import API
import time

# ==========================================================
# Config – change this to hunt a different mob
# ==========================================================
TARGET_NAME = "Seraphi"       # case-insensitive partial match
SCAN_RANGE = 18
MELEE_RANGE = 2
TELEPORT_COOLDOWN = 1.0       # seconds between cast attempts
MAX_OFFSET = 6                # stop increasing past this
# ==========================================================

last_teleport = 0.0
teleport_offset = 1
target_lower = TARGET_NAME.lower()

OFFSET_RING = [
    ( 1,  0), (-1,  0), ( 0,  1), ( 0, -1),
    ( 1,  1), ( 1, -1), (-1,  1), (-1, -1),
]

BLOCKED_MSGS = [
    "That location is blocked.",
    "That is too far away",
]

API.SysMsg(f"Hunting: {TARGET_NAME}", 1150)

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    # Blocked / too far → bump offset and retry
    if API.InJournalAny(BLOCKED_MSGS, clearMatches=True):
        teleport_offset = min(teleport_offset + 1, MAX_OFFSET)
        API.SysMsg(f"Bad teleport tile – offset now {teleport_offset}", 53)
        last_teleport = 0.0

    target = None
    mobs = API.NearestMobiles(
        [
            API.Notoriety.Gray,
            API.Notoriety.Criminal,
            API.Notoriety.Enemy,
            API.Notoriety.Murderer,
        ],
        SCAN_RANGE
    )

    if mobs:
        for m in mobs:
            if not m or m.IsDead:
                continue
            name = m.Name.lower() if m.Name else ""
            if target_lower in name:
                target = m
                break

    if target:
        if target.Distance > MELEE_RANGE:
            if now - last_teleport >= TELEPORT_COOLDOWN and not API.Player.IsCasting:
                idx = (teleport_offset - 1) % len(OFFSET_RING)
                dx, dy = OFFSET_RING[idx]
                dx *= teleport_offset
                dy *= teleport_offset

                API.CastSpell("Teleport")
                if API.WaitForTarget("any", 2.0):
                    API.Target(target.X + dx, target.Y + dy, target.Z)
                last_teleport = now
        else:
            teleport_offset = 1

        API.Attack(target.Serial)
    else:
        teleport_offset = 1

    time.sleep(0.2)

API.SysMsg("Hunter offline", 1150)