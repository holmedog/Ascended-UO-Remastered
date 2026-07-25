import API
import time

# ==========================================================
# Waypoints (x, y, z) – ends back at start, then idles & repeats
# ==========================================================
WAYPOINTS = [
    (5844, 917, -20),
    (5834, 917, -20),
    (5833, 927, -20),
    (5834, 940, -20),
    (5833, 927, -20),
    (5845, 927, -20),  
    (5844, 940, -20),
    (5845, 927, -20),  
    (5859, 927, -20), 
    (5845, 927, -20),  # return home
]

ARRIVE_DIST = 2
STEP_DIST = 10
LOOP_DELAY = 0.25
STUCK_TIME = 1.5
IDLE_SECONDS = 20
MAX_STUCK_RETRIES = 6

DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]
OFFSETS = [
    (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
    (2, 0), (-2, 0), (0, 2), (0, -2),
]
# ==========================================================

wp_index = 0
stuck_count = 0
offset_idx = 0
last_pos = (API.Player.X, API.Player.Y)
last_move_time = time.time()

_seed = int(time.time()) & 0x7FFFFFFF

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
    # Nudge mid-point too so we don't always hit the same blocked tile
    mx += ox
    my += oy
    API.Pathfind(mx, my, tz, 0, False)

API.SysMsg(f"Waypoint run started ({len(WAYPOINTS)} points)", 1150)

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    if wp_index >= len(WAYPOINTS):
        if API.Pathfinding():
            API.CancelPathfinding()
        API.SysMsg(f"Route complete – idling {IDLE_SECONDS}s", 68)
        idle_end = time.time() + IDLE_SECONDS
        while not API.StopRequested and time.time() < idle_end:
            API.ProcessCallbacks()
            time.sleep(0.25)
        wp_index = 0
        stuck_count = 0
        offset_idx = 0
        last_move_time = time.time()
        API.SysMsg("Restarting route", 1150)
        continue

    tx, ty, tz = WAYPOINTS[wp_index]

    if near(tx, ty):
        API.SysMsg(f"Reached waypoint {wp_index + 1}/{len(WAYPOINTS)}", 68)
        wp_index += 1
        stuck_count = 0
        offset_idx = 0
        if API.Pathfinding():
            API.CancelPathfinding()
        last_move_time = now
        continue

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

        # Physical shove off the blocked tile
        API.Run(DIRECTIONS[rnd(8)])
        time.sleep(0.3)

        # Try a different approach angle next pathfind
        offset_idx += 1
        last_move_time = time.time()

        # Give up on this waypoint after too many failures
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