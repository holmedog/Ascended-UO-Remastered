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

MAX_DIST = 8 
MIN_DIST = 3

SCAN_RANGE = 12
ROAM_RANGE = 12
ROAM_VARIANCE = 2 # This is a percent; it's how often you want to chance changing directions without hitting walls
MELEE_RANGE = 1
LOOP_DELAY = 0.20
STUCK_TIME = 2.5
BLACKLIST_TIME = 30
SAFETY_CHECK = 0.3          # pause after pathfind and verify we actually moved
ROAM = True

DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]

# path_serial = what we are pathfinding toward (sticky)
# attack_serial = what we currently Attack() (can change every scan)
path_serial = 0
attack_serial = 0
move_mode = "idle"  # chase / melee / roam / idle
roam_target = None
last_roam_dir = None
last_pos = (0, 0)
last_move_time = time.time()
unreachable = {}  # serial -> time we can try it again
need_new_dir = False

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
    if dx > 0 and dy < 0:
        return 1
    if dx > 0 and dy > 0:
        return 3
    if dx < 0 and dy > 0:
        return 5
    return 7


def roam_point():
    global last_roam_dir
    if last_roam_dir is None or rnd(100) < ROAM_VARIANCE:
        last_roam_dir = rnd(8)
    # else: keep the exact same direction
    dist = MIN_DIST + rnd(MAX_DIST - MIN_DIST + 1)
    dx = [0, 1, 1, 1, 0, -1, -1, -1][last_roam_dir] * dist
    dy = [-1, -1, 0, 1, 1, 1, 0, -1][last_roam_dir] * dist
    API.SysMsg(f"Pathing {DIRECTIONS[last_roam_dir]}", 88)
    return (API.Player.X + dx, API.Player.Y + dy)


def force_new_direction():
    """Force a different roam direction (used by safety check / stuck recovery)."""
    global last_roam_dir
    if last_roam_dir is None:
        last_roam_dir = rnd(8)
    else:
        # pick a clearly different direction (±2..±4 steps)
        offset = rnd(3) + 2  # 2, 3 or 4
        if rnd(2):
            offset = -offset
        last_roam_dir = (last_roam_dir + offset) % 8
    return last_roam_dir


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


def pathfind_with_safety(pathfind_fn, *args, **kwargs):
    """
    Call a pathfind function, wait SAFETY_CHECK, and verify we moved.
    If we did not move, cancel pathfinding and flag that the next
    roam attempt should use a different direction (after a mob scan).
    Returns True if movement was detected, False otherwise.
    """
    global roam_target, last_move_time, need_new_dir

    start_pos = (API.Player.X, API.Player.Y)
    pathfind_fn(*args, **kwargs)

    time.sleep(SAFETY_CHECK)
    API.ProcessCallbacks()

    new_pos = (API.Player.X, API.Player.Y)
    if new_pos != start_pos:
        last_move_time = time.time()
        return True

    # no movement → abort and let next loop re-scan for mobs first
    if API.Pathfinding():
        API.CancelPathfinding()
    roam_target = None
    need_new_dir = True          # force different direction on next roam
    last_move_time = time.time()
    API.SysMsg("Path safety: no move – will try new dir next", 53)
    return False

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
        force_new_direction()          # use the same direction-change logic
        API.Run(DIRECTIONS[last_roam_dir])
        roam_target = None
        last_move_time = now

    elif desired == "chase":
        if not API.Pathfinding():
            # PathfindEntity with safety check
            API.SysMsg(f"Pathing to and attacking: [{path_enemy.Name}]", 88)   # ← here
            moved = pathfind_with_safety(
                API.PathfindEntity,
                path_enemy.Serial, MELEE_RANGE, False
            )
            if not moved and path_enemy:
                last_roam_dir = dir_to_target(path_enemy.X, path_enemy.Y)
                need_new_dir = True   # instead of force_new_direction() here
        if path_enemy and path_enemy.Distance > MELEE_RANGE + 1:
            last_roam_dir = dir_to_target(path_enemy.X, path_enemy.Y)

    elif desired == "roam":
        if (roam_target is None
                or near_point(roam_target[0], roam_target[1])
                or not API.Pathfinding()):
            if need_new_dir:
                force_new_direction()
                need_new_dir = False
            roam_target = roam_point()
            pathfind_with_safety(
                API.Pathfind,
                roam_target[0], roam_target[1], API.Player.Z, 0, False
            )

    elif desired == "melee":
        if API.Pathfinding():
            API.CancelPathfinding()

    # ----------------------------------
    # Attack – always the best scanned target (can differ from path target)
    # ----------------------------------
    if attack_enemy:
        if attack_serial != attack_enemy.Serial:          # only on change
            API.SysMsg(f"Attacking {attack_enemy.Name} while pathing", 88)
        API.Attack(attack_enemy.Serial)

    if not API.PrimaryAbilityActive():
        API.ToggleAbility("primary")

    time.sleep(LOOP_DELAY)

API.SysMsg("Lone Wolf Hunt offline", 1150)