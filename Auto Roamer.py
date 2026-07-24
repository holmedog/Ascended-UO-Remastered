import API
import time
# ==========================================================
# Lone Wolf - Pure Hunt + Roam
#
# Target priority + attack + roam only.
# No healing, buffs, potions, feeding, or corpse grabbing.
# ==========================================================
SCAN_RANGE = 12
ROAM_RANGE = 18
MELEE_RANGE = 1
LOOP_DELAY = 0.20
STUCK_TIME = 2.5
BLACKLIST_TIME = 30
ROAM = True
DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]
current_target_serial = 0
move_mode = "idle" # chase / melee / roam / idle
roam_target = None
last_roam_dir = None
last_pos = (0, 0)
last_move_time = time.time()
unreachable = {} # serial -> time we can try it again
# tiny RNG so we don't depend on the random module
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
    # Prefer cardinal if one axis dominates a lot, otherwise diagonal
    if adx > ady * 2:          # mostly east/west
        return 2 if dx > 0 else 6
    if ady > adx * 2:          # mostly north/south
        return 0 if dy < 0 else 4
    # diagonal
    if dx > 0 and dy < 0: return 1   # NE
    if dx > 0 and dy > 0: return 3   # SE
    if dx < 0 and dy > 0: return 5   # SW
    return 7                         # NW

def roam_point():
    global last_roam_dir
    # Rarely change direction (keeps long straight legs). 15% chance of full new direction.
    if last_roam_dir is None or rnd(100) < 15:
        last_roam_dir = rnd(8)
    else:
        # Tiny deviation so it is not perfectly locked forever
        last_roam_dir = (last_roam_dir + rnd(3) - 1) % 8
    # Longer legs = straighter travel
    dist = 16 + rnd(10) # 16-25 tiles
    # 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
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

API.SysMsg("Lone Wolf Hunt online", 1150)
# ==========================================================
# Main Loop
# ==========================================================
while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()
    # ----------------------------------
    # Scan nearby hostiles
    # ----------------------------------
    hostiles = API.NearestMobiles(
        [
            API.Notoriety.Gray,
            API.Notoriety.Criminal,
            API.Notoriety.Enemy,
            API.Notoriety.Murderer
        ],
        SCAN_RANGE
    )
    elite_paragon = None
    elite_only = None
    paragon_only = None
    if hostiles:
        for m in hostiles:
            if not m or m.IsDead:
                continue
            nm = m.Name.lower() if m.Name else ""
            is_para = "paragon" in nm
            is_elite = "elite" in nm
            if not is_blacklisted(m.Serial):
                if is_elite and is_para:
                    if not elite_paragon or m.Distance < elite_paragon.Distance:
                        elite_paragon = m
                elif is_elite:
                    if not elite_only or m.Distance < elite_only.Distance:
                        elite_only = m
                elif is_para:
                    if not paragon_only or m.Distance < paragon_only.Distance:
                        paragon_only = m
    # ----------------------------------
    # Find target (priority: elite paragon > elite > paragon > nearest)
    # ----------------------------------
    pos = (API.Player.X, API.Player.Y)
    if pos != last_pos:
        last_pos = pos
        last_move_time = now
    stuck = (now - last_move_time) >= STUCK_TIME
    enemy = None
    # reuse current target if still alive
    if current_target_serial:
        enemy = API.FindMobile(current_target_serial)
    if not enemy or enemy.IsDead:
        current_target_serial = 0
        enemy = None
    if elite_paragon:
        enemy = elite_paragon
    elif elite_only:
        enemy = elite_only
    elif paragon_only:
        enemy = paragon_only
    if not enemy:
        cands = API.NearestMobiles(
            [
                API.Notoriety.Gray,
                API.Notoriety.Criminal,
                API.Notoriety.Enemy,
                API.Notoriety.Murderer
            ],
            ROAM_RANGE
        )
        if cands:
            for m in cands:
                if not m or m.IsDead or is_blacklisted(m.Serial):
                    continue
                if enemy is None or m.Distance < enemy.Distance:
                    enemy = m
    if enemy:
        current_target_serial = enemy.Serial
    # ----------------------------------
    # Movement
    # ----------------------------------
    API.Msg("[grab")
    if enemy and enemy.Distance > MELEE_RANGE:
        desired = "chase"
    elif enemy:
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
    if stuck and desired == "chase" and enemy:
        # unreachable - blacklist and drop
        API.CancelPathfinding()
        unreachable[enemy.Serial] = now + BLACKLIST_TIME
        API.SysMsg("No path to target - skipping", 53)
        current_target_serial = 0
        enemy = None
        last_move_time = now
    elif stuck and desired == "roam":
        # blocked while roaming - shove and reset direction
        API.CancelPathfinding()
        API.Run(DIRECTIONS[rnd(8)])
        roam_target = None
        last_roam_dir = None
        last_move_time = now
    elif desired == "chase":
        if not API.Pathfinding():
            API.PathfindEntity(enemy.Serial, MELEE_RANGE, False)
        # Keep roam heading roughly the same way we were chasing
        if enemy.Distance > MELEE_RANGE + 1:
            last_roam_dir = dir_to_target(enemy.X, enemy.Y)
    elif desired == "roam":
        if roam_target is None or near_point(roam_target[0], roam_target[1]) or not API.Pathfinding():
            roam_target = roam_point()
            API.Pathfind(roam_target[0], roam_target[1], API.Player.Z, 0, False)
    elif desired == "melee":
        if API.Pathfinding():
            API.CancelPathfinding()
    # ----------------------------------
    # Attack
    # ----------------------------------
    if enemy:
        API.Attack(enemy.Serial)
    if not API.PrimaryAbilityActive():
        API.ToggleAbility("primary")
       
       
API.SysMsg("Lone Wolf Hunt offline", 1150)