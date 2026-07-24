import API
import time

# ==========================================================
# Standalone Smart Target Selector + Auto Attack
# ==========================================================

SCAN_RANGE = 12

use_hostile_outlines = True
use_paragon_markers = True

HUE_PARAGON = 1150
seen_paragons = []
current_target_serial = 0
last_hostile_time = time.time()
dormant = False
last_loop_time = time.time()   # For loop timing debug


def is_valid_mobile(mobile):
    return mobile and not getattr(mobile, 'IsDead', True)


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

    best = elite_paragon or elite_only or paragon_only or nearest_other
    return best


API.SysMsg("Smart Target Selector Started", 68)

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    # Only scan if we don't have a valid current target
    if current_target_serial:
        enemy = API.FindMobile(current_target_serial)
        if is_valid_mobile(enemy):
            API.Attack(enemy.Serial)
            API.Pause(0.3)
            continue

    # Scan for new targets
    hostiles = API.NearestMobiles(
        [API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Enemy, API.Notoriety.Murderer],
        SCAN_RANGE
    )

    if hostiles:
        last_hostile_time = now
        if dormant:
            dormant = False
    else:
        if now - last_hostile_time >= 8:
            dormant = True
        API.Pause(0.4)
        continue

    enemy = choose_enemy_from_hostiles(hostiles)

    if enemy:
        current_target_serial = enemy.Serial
        API.Attack(enemy.Serial)

    API.Pause(0.3)

API.SysMsg("Smart Target Selector Stopped")