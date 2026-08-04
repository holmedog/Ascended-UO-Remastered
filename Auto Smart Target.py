import API
import time

# ==========================================================
# Standalone Smart Target Selector + Auto Attack
# ==========================================================
SCAN_RANGE = 12
CLOSEST_SCAN_RANGE = 7          # only used when use_closest_target is True
use_hostile_outlines = True
use_paragon_markers = True
use_closest_target = True        # ← set True for continuous closest-target mode
HUE_PARAGON = 1150

seen_paragons = []
current_target_serial = 0
last_hostile_time = time.time()
dormant = False

def is_valid_mobile(mobile):
    return mobile and not getattr(mobile, "IsDead", True)

def choose_enemy_from_hostiles(hostiles):
    elite_paragon = None
    elite_only = None
    paragon_only = None
    nearest_other = None

    for m in hostiles:
        if not is_valid_mobile(m):
            continue

        nm = m.Name.lower() if m.Name else ""
        is_para = "paragon" in nm
        is_elite = "elite" in nm

        if use_hostile_outlines:
            if m.Name and "Paragon" in m.Name:
                color = "#FF00FF"
            elif m.Notoriety in (API.Notoriety.Murderer, API.Notoriety.Enemy):
                color = "#FF2020" if m.Distance <= 3 else "#FF8000"
            elif m.Notoriety == API.Notoriety.Criminal:
                color = "#FFD000"
            else:
                color = "#B0B0B0"
            m.SetOutlineColor(color)

        if is_elite and is_para:
            if not elite_paragon or m.Distance < elite_paragon.Distance:
                elite_paragon = m
        elif is_elite:
            if not elite_only or m.Distance < elite_only.Distance:
                elite_only = m
        elif is_para:
            if not paragon_only or m.Distance < paragon_only.Distance:
                paragon_only = m
        else:
            if not nearest_other or m.Distance < nearest_other.Distance:
                nearest_other = m

        if is_para and use_paragon_markers and m.Serial not in seen_paragons:
            seen_paragons.append(m.Serial)
            API.SysMsg("PARAGON: " + (m.Name or "Unknown"), HUE_PARAGON)
            API.HeadMsg("PARAGON", m.Serial, HUE_PARAGON)
            API.AddMapMarker("Paragon: " + (m.Name or "Unknown"), m.X, m.Y, API.GetMap(), "purple")

    return elite_paragon or elite_only or paragon_only or nearest_other

API.SysMsg("Smart Target Selector Started", 68)

while not API.StopRequested:
    API.ProcessCallbacks()

    # ----------------------------------------------------------
    # CLOSEST-TARGET MODE – re-evaluate every tick, never stick
    # ----------------------------------------------------------
    if use_closest_target:
        enemy = API.NearestMobile(
            [
                API.Notoriety.Gray,
                API.Notoriety.Criminal,
                API.Notoriety.Murderer,
                API.Notoriety.Enemy,
            ],
            CLOSEST_SCAN_RANGE,
        )

        if is_valid_mobile(enemy):
            current_target_serial = enemy.Serial
            API.Attack(enemy.Serial)          # always re-issue so client stays on it
            last_hostile_time = time.time()
            dormant = False
        else:
            current_target_serial = 0
            if time.time() - last_hostile_time >= 8:
                dormant = True

        continue

    # ----------------------------------------------------------
    # SMART / PRIORITY MODE – stick to current target while valid
    # ----------------------------------------------------------
    now = time.time()

    if current_target_serial:
        enemy = API.FindMobile(current_target_serial)
        if is_valid_mobile(enemy):
            API.Attack(enemy.Serial)
            API.Pause(0.1)
            continue

    hostiles = API.NearestMobiles(
        [API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Enemy, API.Notoriety.Murderer],
        SCAN_RANGE,
    )

    if hostiles:
        last_hostile_time = now
        if dormant:
            dormant = False
    else:
        if now - last_hostile_time >= 8:
            dormant = True
        API.Pause(0.2)
        continue

    enemy = choose_enemy_from_hostiles(hostiles)

    if enemy:
        current_target_serial = enemy.Serial
        API.Attack(enemy.Serial)


API.SysMsg("Smart Target Selector Stopped")