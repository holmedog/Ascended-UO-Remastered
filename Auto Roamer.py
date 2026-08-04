import API
import time
# ==========================================================
# Lone Wolf - Pure Hunt + Roam
#
# Target priority + attack + roam only.
# No healing, buffs, potions, feeding, or corpse grabbing.
#
# Attack target and path target are separate:
# - Always re-scan and attack the best target each loop
# - Pathfinding continues to the original chase target
# ==========================================================
SCAN_RANGE = 12
ROAM_RANGE = 12
MELEE_RANGE = 1
LOOP_DELAY = 0.20
STUCK_TIME = 2.5
BLACKLIST_TIME = 30
ROAM = True
DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]

# path_serial  = what we are pathfinding toward (sticky)
# attack_serial = what we currently Attack() (can change every scan)
path_serial = 0
attack_serial = 0
move_mode = "idle"  # chase / melee / roam / idle
roam_target = None
last_roam_dir = None
last_pos = (0, 0)
last_move_time = time.time()
unreachable = {}  # serial -> time we can try it again

_seed = int(time.time()) & 0x7FFFFFFF

# ==========================================================
# Defs
# ==========================================================
def rnd(n):
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed % n

def dir_to_target(tx, ty):
    """Return 0-7 direction index toward (tx, ty) from player."""
    dx = tx - API.Player.X
    dy = ty - API.Player.Y
    if dx == 0 and dy == 0:
        return last_roam_dir if last_roam_dir is not None else 0
    adx = abs(dx)
    ady = abs(dy)
    if adx > ady * 2:
        return 2 if dx > 0 else 6
    if ady > adx * 2:
        return 0 if dy < 0 else 4
    if dx > 0 and dy < 0: return 1
    if dx > 0 and dy > 0: return 3
    if dx < 0 and dy > 0: return 5
    return 7

def roam_point():
    global last_roam_dir
    if last_roam_dir is None or rnd(100) < 5:
        last_roam_dir = rnd(8)
    else:
        last_roam_dir = (last_roam_dir + rnd(3) - 1) % 8
    dist = 16 + rnd(10)
    dx = [ 0, 1, 1, 1, 0, -1, -1, -1][last_roam_dir] * dist
    dy = [-1, -1, 0, 1, 1, 1, 0, -1][last_roam_dir] * dist
    return (API.Player.X + dx, API.Player.Y + dy)

def near_point(tx, ty):
    return abs(API.Player.X - tx) <= 1 and abs(API.Player.Y - ty) <= 1

def is_blacklisted(serial):
    exp = unreachable.get(serial)
    if exp is None:
        return False
    if time.time() >= exp:
        del unreachable[serial]
        return False
    return True

def pick_best_enemy(range_tiles):
    """Always scan and return best living non-blacklisted hostile in range.
    Priority: elite+paragon > elite > paragon > nearest.
    """
    hostiles = API.NearestMobiles(
        [
            API.Notoriety.Gray,
            API.Notoriety.Criminal,
            API.Notoriety.Enemy,
            API.Notoriety.Murderer
        ],
        range_tiles
    )
    elite_paragon = None
    elite_only = None
    paragon_only = None
    nearest = None

    if hostiles:
        for m in hostiles:
            if not m or m.IsDead or is_blacklisted(m.Serial):
                continue
            nm = m.Name.lower() if m.Name else ""
            is_para = "paragon" in nm
            is_elite = "elite" in nm

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
                if nearest is None or m.Distance < nearest.Distance:
                    nearest = m

    if elite_paragon:
        return elite_paragon
    if elite_only:
        return elite_only
    if paragon_only:
        return paragon_only
    return nearest

API.SysMsg("Lone Wolf Hunt online", 1150)

# ==========================================================
# Main Loop
# ==========================================================
while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    # ----------------------------------
    # Always re-scan (attack target can change every tick)
    # ----------------------------------
    attack_enemy = pick_best_enemy(SCAN_RANGE)
    if not attack_enemy:
        # widen scan a bit when nothing close
        attack_enemy = pick_best_enemy(ROAM_RANGE)

    if attack_enemy:
        attack_serial = attack_enemy.Serial
    else:
        attack_serial = 0

    # ----------------------------------
    # Resolve path target (sticky – only changes when invalid)
    # ----------------------------------
    path_enemy = None
    if path_serial:
        path_enemy = API.FindMobile(path_serial)
        if not path_enemy or path_enemy.IsDead or is_blacklisted(path_serial):
            path_serial = 0
            path_enemy = None

    # If we have no path target, adopt the current attack target
    if not path_enemy and attack_enemy:
        path_serial = attack_enemy.Serial
        path_enemy = attack_enemy

    # ----------------------------------
    # Stuck detection
    # ----------------------------------
    pos = (API.Player.X, API.Player.Y)
    if pos != last_pos:
        last_pos = pos
        last_move_time = now
    stuck = (now - last_move_time) >= STUCK_TIME

    # ----------------------------------
    # Decide desired movement mode from PATH target
    # ----------------------------------
    if path_enemy and path_enemy.Distance > MELEE_RANGE:
        desired = "chase"
    elif path_enemy:
        desired = "melee"
    elif ROAM:
        desired = "roam"
    else:
        desired = "idle"

    # mode change -> cancel old path
    if desired != move_mode:
        if API.Pathfinding():
            API.CancelPathfinding()
        roam_target = None
        move_mode = desired

    # ----------------------------------
    # Movement execution
    # ----------------------------------
    API.Msg("[grab")

    if stuck and desired == "chase" and path_enemy:
        API.CancelPathfinding()
        unreachable[path_enemy.Serial] = now + BLACKLIST_TIME
        API.SysMsg("No path to target - skipping", 53)
        path_serial = 0
        path_enemy = None
        last_move_time = now
        # attack_serial stays – we may still be hitting something else

    elif stuck and desired == "roam":
        API.CancelPathfinding()
        API.Run(DIRECTIONS[rnd(8)])
        roam_target = None
        last_roam_dir = None
        last_move_time = now

    elif desired == "chase":
        if not API.Pathfinding():
            API.PathfindEntity(path_enemy.Serial, MELEE_RANGE, False)
        if path_enemy.Distance > MELEE_RANGE + 1:
            last_roam_dir = dir_to_target(path_enemy.X, path_enemy.Y)

    elif desired == "roam":
        if roam_target is None or near_point(roam_target[0], roam_target[1]) or not API.Pathfinding():
            roam_target = roam_point()
            API.Pathfind(roam_target[0], roam_target[1], API.Player.Z, 0, False)

    elif desired == "melee":
        if API.Pathfinding():
            API.CancelPathfinding()

    # ----------------------------------
    # Attack – always the best scanned target (can differ from path target)
    # ----------------------------------
    if attack_enemy:
        API.Attack(attack_enemy.Serial)


API.SysMsg("Lone Wolf Hunt offline", 1150)