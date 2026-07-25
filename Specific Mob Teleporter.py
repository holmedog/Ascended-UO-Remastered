import API
import time

# ==========================================================
# Config – change this to hunt a different mob
# ==========================================================
TARGET_NAME = "Seraphi"   # case-insensitive partial match
SCAN_RANGE = 18
MELEE_RANGE = 2
TELEPORT_COOLDOWN = 1.0               # seconds between cast attempts
# ==========================================================

last_teleport = 0.0
target_lower = TARGET_NAME.lower()

API.SysMsg(f"Hunting: {TARGET_NAME}", 1150)

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

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
                API.CastSpell("Teleport")
                if API.WaitForTarget("any", 2.0):
                    API.Target(target.X + 1, target.Y + 1, target.Z)
                last_teleport = now
        API.Attack(target.Serial)

    time.sleep(0.2)

API.SysMsg("Hunter offline", 1150)