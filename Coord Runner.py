import API
import time

# ==========================================================
# Options (edit these)
# ==========================================================
ARRIVE_DIST = 2            # when you consider yourself at the waypoint
CAST_SPELL = False         # True = cast Chain Lightning at each stop
STEP_DIST = 16             # if farther than this, take a mid-step
LOOP_DELAY = 0.05          # throttle between pathing attempts
STUCK_TIME = 1.5           # how long before considering yourself stuck
STAY_TIME = 0              # pause at each waypoint (0 = no stop)
IDLE_SECONDS = 8           # idle time at end of route
MAX_STUCK_RETRIES = 6
GRAB_DELAY = 2             # how often to send [grab
SCAN_HOSTILES = True      #Stop on hostiles within SCAN_RANGE
SCAN_RANGE = 3

PULL_PETS_MODE = "hostile"
# Pull followers mode:
#   "end"     → only at the end of the route
#   "hostile" → when a hostile is detected
#   "never"   → disabled

HOSTILE_NOTORIETIES = [
    API.Notoriety.Gray,
    API.Notoriety.Criminal,
    API.Notoriety.Enemy,
    API.Notoriety.Murderer,
]

DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]
OFFSETS = [
    (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
    (2, 0), (-2, 0), (0, 2), (0, -2),
]
# ==========================================================

def load_waypoints(path):
    points = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().rstrip(",")
                if not line or not line.startswith("("):
                    continue
                coords = line[1:-1].split(",")
                if len(coords) == 3:
                    x = int(coords[0].strip())
                    y = int(coords[1].strip())
                    z = int(coords[2].strip())
                    points.append((x, y, z))
    except Exception as e:
        API.SysMsg(f"Failed to load waypoints: {e}", 33)
        return []
    return points

WAYPOINTS = load_waypoints(API.ScriptPath + "/waypoints.txt")

if not WAYPOINTS:
    API.SysMsg("No waypoints found in waypoints.txt – stopping", 33)

wp_index = 0
stuck_count = 0
offset_idx = 0
last_pos = (API.Player.X, API.Player.Y)
last_move_time = time.time()
last_grab_time = time.time()
_seed = int(time.time()) & 0x7FFFFFFF
was_waiting_for_clear = False

def rnd(n):
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed % n

def dist_to(x, y):
    return max(abs(API.Player.X - x), abs(API.Player.Y - y))

def near(x, y, d=ARRIVE_DIST):
    return dist_to(x, y) <= d

def step_toward(tx, ty, tz):
    """Pathfind toward target; use mid-step if far. Apply small offset on retries."""
    ox, oy = OFFSETS[offset_idx % len(OFFSETS)]
    goal_x = tx + ox
    goal_y = ty + oy
    d = dist_to(goal_x, goal_y)
    if d <= STEP_DIST:
        API.Pathfind(goal_x, goal_y, tz, 0, False)
        return
    px, py = API.Player.X, API.Player.Y
    ratio = STEP_DIST / float(d)
    mx = int(px + (goal_x - px) * ratio)
    my = int(py + (goal_y - py) * ratio)
    mx += ox
    my += oy
    API.Pathfind(mx, my, tz, 0, False)

def has_hostile_nearby():
    if not SCAN_HOSTILES:
        return False
    enemy = API.NearestMobile(HOSTILE_NOTORIETIES, SCAN_RANGE)
    return enemy is not None

def pull_followers():
    """Use the ball / command to pull pets in and set them to guard."""
    API.UseType(0xe2e, 2000)
    API.Pause(1)
    API.Msg("all guard me")
    API.SysMsg("Pulled followers", 68)

API.SysMsg(f"Waypoint run started ({len(WAYPOINTS)} points)", 1150)
if SCAN_HOSTILES:
    API.SysMsg(f"Hostile scan ON – range {SCAN_RANGE}", 68)
API.SysMsg(f"Pull pets mode: {PULL_PETS_MODE}", 68)

while not API.StopRequested and WAYPOINTS:
    API.ProcessCallbacks()
    now = time.time()

    if now - last_grab_time >= GRAB_DELAY:
        API.Msg("[grab")
        last_grab_time = time.time()

    # ----- Hostile check -----
    if has_hostile_nearby():
        if API.Pathfinding():
            API.CancelPathfinding()
        if not was_waiting_for_clear:
            API.SysMsg("Hostile detected – holding position", 33)
            was_waiting_for_clear = True
            if PULL_PETS_MODE == "hostile":
                pull_followers()
        time.sleep(0.5)
        continue
    else:
        if was_waiting_for_clear:
            API.SysMsg("Area clear – resuming route", 68)
            was_waiting_for_clear = False
            last_move_time = time.time()

    # ----- Route finished → idle & restart -----
    if wp_index >= len(WAYPOINTS):
        if API.Pathfinding():
            API.CancelPathfinding()
        API.SysMsg(f"Route complete – idling {IDLE_SECONDS}s", 68)

        if PULL_PETS_MODE == "end":
            pull_followers()

        idle_end = time.time() + IDLE_SECONDS
        while not API.StopRequested and time.time() < idle_end:
            API.ProcessCallbacks()
            if has_hostile_nearby():
                break
            time.sleep(0.05)

        wp_index = 0
        stuck_count = 0
        offset_idx = 0
        last_move_time = time.time()
        API.SysMsg("Restarting route", 1150)
        continue

    tx, ty, tz = WAYPOINTS[wp_index]

    # ----- Arrived at waypoint -----
    if near(tx, ty):
        if CAST_SPELL:
            API.CastSpell("chain lightning")
        if STAY_TIME > 0:
            API.Pause(STAY_TIME)
        API.SysMsg(f"Reached waypoint {wp_index + 1}/{len(WAYPOINTS)}", 68)
        wp_index += 1
        stuck_count = 0
        offset_idx = 0
        if API.Pathfinding():
            API.CancelPathfinding()
        last_move_time = now
        continue

    # ----- Movement / stuck detection -----
    pos = (API.Player.X, API.Player.Y)
    if pos != last_pos:
        last_pos = pos
        last_move_time = now
        stuck_count = 0

    if now - last_move_time >= STUCK_TIME:
        stuck_count += 1
        API.SysMsg(f"Stuck at {pos[0]},{pos[1]} – recovery {stuck_count}", 53)
        if API.Pathfinding():
            API.CancelPathfinding()
        API.Run(DIRECTIONS[rnd(8)])
        time.sleep(0.1)
        offset_idx += 1
        last_move_time = time.time()
        if stuck_count >= MAX_STUCK_RETRIES:
            API.SysMsg(f"Skipping waypoint {wp_index + 1} – unreachable", 33)
            wp_index += 1
            stuck_count = 0
            offset_idx = 0
        continue

    if not API.Pathfinding():
        step_toward(tx, ty, tz)

    time.sleep(LOOP_DELAY)

API.SysMsg("Waypoint run offline", 1150)