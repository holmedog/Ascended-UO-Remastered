import API
import time
# ==========================================================
# Lone Wolf - Solo Guardian + Threat Radar
#
# For solo leveling with NO companions. Hunts down the nearest
# creature, runs to it at full speed (pathfinding), fights,
# heals, wanders to find more, and flees when low.
#
# Priority:
# 1. Dead -> [res
# 2. Poison -> Cleanse by Fire
# 3. Critical -> flee + Greater Heal
# 4. HP <= 85 -> Greater Heal
# 5. Idle -> buffs + feed + potions (10 min)
#
# Outlines: paragon = magenta, murderer = red, enemy = orange,
# criminal = yellow, gray = gray.
#
# Targets: elite paragon > elite > paragon > nearest.
# ==========================================================
SCAN_RANGE = 12
ENGAGE_RANGE = 10
ROAM_RANGE = 12 # how far to look for a creature to run to
MELEE_RANGE = 1 # this close = stop and swing
FLEE_DIST = 8 # how far to path away when fleeing
CHECK_DELAY = 0.40 # spell cast -> target timing
LOOP_DELAY = 0.20 # loop pacing (pathfinding moves continuously anyway)
HEAL_PERCENT = 85
CRITICAL_PERCENT = 45
CURE_SPELL = "Cleanse by Fire"
HEAL_SPELL = "Greater Heal"
BUFF_DELAY = 8
FEED_DELAY = 30
CAST_BUFFS = False

# potions - fire both on a 10 minute timer
POTION_DELAY = 600 # 10 minutes
POTION_GAP = 5 # seconds between the two potions
STAR_POTION = 0x40271C3B # Star Potion (item serial)
GREED_POTION = 0x400C1FED # Potion of Greed (item serial)
# hues
HUE_INFO = 88
HUE_GOOD = 68
HUE_WARN = 53
HUE_DANGER = 33
HUE_PARAGON = 1150
# extras
ROAM = True # wander to find mobs when none are near
RING_DELAY = 3 # how often to redraw the range ring
GRAB_DELAY = 10 # [grab corpses no more than this often (seconds)
STUCK_TIME = 2.5 # no movement this long while moving = stuck
BLACKLIST_TIME = 30 # ignore an unreachable target for this long (seconds)
DIRECTIONS = ["north", "northeast", "east", "southeast",
              "south", "southwest", "west", "northwest"]
last_buff_time = 0
last_feed_time = 0
last_potion_time = 0
last_ring_time = 0
last_grab_time = 0
current_target_serial = 0
seen_paragons = []
was_dead = False
move_mode = "idle" # flee / chase / melee / roam / idle
roam_target = None
last_roam_dir = None          # 0-7, persists across hops for straighter lines
last_pos = (0, 0)
last_move_time = time.time()
unreachable = {} # serial -> time we can try it again
def hp_percent():
    if API.Player.HitsMax <= 0:
        return 100
    return (API.Player.Hits * 100.0) / API.Player.HitsMax
# tiny RNG so we don't depend on the random module
_seed = int(time.time()) & 0x7FFFFFFF
def rnd(n):
    global _seed
    _seed = (_seed * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed % n
def roam_point():
    global last_roam_dir
    # Rarely change direction (keeps long straight legs). 15% chance of full new direction.
    if last_roam_dir is None or rnd(100) < 15:
        last_roam_dir = rnd(8)
    else:
        # Tiny deviation so it is not perfectly locked forever
        last_roam_dir = (last_roam_dir + rnd(3) - 1) % 8
    # Longer legs = straighter travel
    dist = 16 + rnd(10)   # 16-25 tiles
    # 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
    dx = [ 0,  1, 1, 1, 0, -1, -1, -1][last_roam_dir] * dist
    dy = [-1, -1, 0, 1, 1,  1,  0, -1][last_roam_dir] * dist
    return (API.Player.X + dx, API.Player.Y + dy)
def flee_point(px, py, ex, ey, dist):
    # a point 'dist' tiles away from (ex, ey)
    sx = 1 if px > ex else (-1 if px < ex else 0)
    sy = 1 if py > ey else (-1 if py < ey else 0)
    if sx == 0 and sy == 0:
        sy = -1
    return (px + sx * dist, py + sy * dist)
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
API.SysMsg("Lone Wolf online", HUE_PARAGON)
while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()
    # ----------------------------------
    # Dead -> resurrect
    # ----------------------------------
    if API.Player.IsDead:
        if not was_dead:
            API.SysMsg("Died - trying to res", HUE_DANGER)
            was_dead = True
        API.Msg("[res")
        API.Pause(2.0)
        current_target_serial = 0
        continue
    if was_dead:
        API.SysMsg("Back up", HUE_GOOD)
        last_buff_time = 0
        was_dead = False
    # ----------------------------------
    # Scan everything nearby and outline it
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
    elite_paragon = None # "elite" + paragon -> primary
    elite_only = None # just "elite" -> secondary
    paragon_only = None # just paragon -> third
    danger = False
    if hostiles:
        for m in hostiles:
            if not m or m.IsDead:
                continue
            # figure out a color for this one
            if m.Name and "Paragon" in m.Name:
                color = "#FF00FF"
            elif m.Notoriety == API.Notoriety.Murderer or m.Notoriety == API.Notoriety.Enemy:
                color = "#FF2020" if m.Distance <= 3 else "#FF8000"
            elif m.Notoriety == API.Notoriety.Criminal:
                color = "#FFD000"
            else:
                color = "#B0B0B0"
            m.SetOutlineColor(color)
            # sort it into a priority bucket (nearest wins each bucket)
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
            # anything nasty right next to me means danger
            if m.Distance <= 4 and (m.Notoriety == API.Notoriety.Murderer or m.Notoriety == API.Notoriety.Enemy or is_para):
                danger = True
            # first time we see a paragon, make some noise
            if is_para:
                if m.Serial not in seen_paragons:
                    seen_paragons.append(m.Serial)
                    API.SysMsg("PARAGON: " + m.Name, HUE_PARAGON)
                    API.HeadMsg("PARAGON", m.Serial, HUE_PARAGON)
                    API.AddMapMarker("Paragon: " + m.Name, m.X, m.Y, API.GetMap(), "purple")
    # ----------------------------------
    # Find target
    # ----------------------------------
    # stuck check - are we actually moving when we mean to?
    pos = (API.Player.X, API.Player.Y)
    if pos != last_pos:
        last_pos = pos
        last_move_time = now
    stuck = (now - last_move_time) >= STUCK_TIME
    critical = hp_percent() <= CRITICAL_PERCENT
    enemy = None
    # reuse the current one if it's still alive
    if current_target_serial:
        enemy = API.FindMobile(current_target_serial)
    # target gone or dead -> drop it so we re-acquire
    if not enemy or enemy.IsDead:
        current_target_serial = 0
        enemy = None
    # priority: elite paragon > elite > paragon > current target > nearest
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
    # Movement - pathfinding moves continuously at full speed
    # ----------------------------------
    if critical and enemy:
        desired = "flee"
    elif enemy and enemy.Distance > MELEE_RANGE:
        desired = "chase"
    elif enemy:
        desired = "melee" # adjacent - hold and swing
    elif ROAM:
        desired = "roam"
    else:
        desired = "idle"
    # changing what we're doing -> drop the old path
    if desired != move_mode:
        if API.Pathfinding():
            API.CancelPathfinding()
        roam_target = None
        move_mode = desired
    if stuck and desired == "chase" and enemy:
        # can't reach this one (wall/water) - blacklist it and move on
        API.CancelPathfinding()
        unreachable[enemy.Serial] = now + BLACKLIST_TIME
        API.SysMsg("No path to target - skipping", HUE_WARN)
        current_target_serial = 0
        enemy = None
        last_move_time = now
    elif stuck and desired in ("flee", "roam"):
        # blocked - break the path and shove off in a random direction
        API.CancelPathfinding()
        API.Run(DIRECTIONS[rnd(8)])
        roam_target = None
        last_roam_dir = None          # force a fresh direction after being stuck
        last_move_time = now
    elif desired == "flee":
        if not API.Pathfinding():
            fp = flee_point(API.Player.X, API.Player.Y, enemy.X, enemy.Y, FLEE_DIST)
            API.Pathfind(fp[0], fp[1], API.Player.Z, 0, False)
    elif desired == "chase":
        if not API.Pathfinding():
            API.PathfindEntity(enemy.Serial, MELEE_RANGE, False)
    elif desired == "roam":
        if roam_target is None or near_point(roam_target[0], roam_target[1]) or not API.Pathfinding():
            roam_target = roam_point()
            API.Pathfind(roam_target[0], roam_target[1], API.Player.Z, 0, False)
    elif desired == "melee":
        if API.Pathfinding():
            API.CancelPathfinding()
    if enemy:
        API.Attack(enemy.Serial)
    if not API.PrimaryAbilityActive():
        API.ToggleAbility("primary")
    if not API.SecondaryAbilityActive():
        API.ToggleAbility("secondary")
    # ----------------------------------
    # [grab corpses (max once every 10s)
    # ----------------------------------
    if now - last_grab_time >= GRAB_DELAY:
        corpse = API.NearestCorpse(2)
        if corpse:
            API.Msg("[grab")
            last_grab_time = now
    # ----------------------------------
    # Priority 1: Cure Poison
    # ----------------------------------
    if API.Player.IsPoisoned:
        API.CastSpell(CURE_SPELL)
        API.Pause(CHECK_DELAY)
        API.TargetSelf()
        continue
    # ----------------------------------
    # Priority 2: Emergency (flee handled above, just heal here)
    # ----------------------------------
    if critical:
        API.SysMsg("CRITICAL - running", HUE_DANGER)
        API.CastSpell(HEAL_SPELL)
        API.Pause(CHECK_DELAY)
        API.TargetSelf()
        continue
    # ----------------------------------
    # Priority 3: Heal
    # ----------------------------------
    if hp_percent() <= HEAL_PERCENT:
        API.CastSpell(HEAL_SPELL)
        API.Pause(CHECK_DELAY)
        API.TargetSelf()
        continue
    current_time = time.time()
    # ----------------------------------
    # Priority 4: Buffs
    # ----------------------------------
    if CAST_BUFFS and current_time - last_buff_time >= BUFF_DELAY and not API.Player.IsPoisoned and hp_percent() > HEAL_PERCENT:
        if not API.BuffExists("Consecrate Weapon"):
            API.CastSpell("Consecrate Weapon")
            API.Pause(CHECK_DELAY)
        if not API.BuffExists("Divine Fury"):
            API.CastSpell("Divine Fury")
            API.Pause(CHECK_DELAY)
        if not API.BuffExists("Enemy of One"):
            API.CastSpell("Enemy of One")
            API.Pause(CHECK_DELAY)
        # these buffs don't take a target, so no TargetSelf - it could grab a
        # stray cursor from another macro. Immolating always recast to refresh.
        API.CastSpell("Immolating Weapon")
        API.Pause(CHECK_DELAY)
        API.CreateCooldownBar(BUFF_DELAY, "Buffs", HUE_INFO)
        last_buff_time = current_time
    # ----------------------------------
    # Feed self - paragons + artifacts (no target needed)
    # ----------------------------------
    if now - last_feed_time >= FEED_DELAY:
        API.Msg("[feedps")
        API.Pause(CHECK_DELAY)
        API.Msg("[feedarti")
        API.Pause(CHECK_DELAY)
        last_feed_time = now
    # ----------------------------------
    # Potions - Star Potion + Potion of Greed every 10 min
    # ----------------------------------
    if now - last_potion_time >= POTION_DELAY:
        API.SysMsg("Using Star Potion", HUE_INFO)
        API.UseObject(STAR_POTION)
        API.Pause(POTION_GAP)
        API.SysMsg("Using Potion of Greed", HUE_INFO)
        API.UseObject(GREED_POTION)
        # visual countdown to the next round
        API.CreateCooldownBar(POTION_DELAY, "Potions", HUE_INFO)
        last_potion_time = now
    # ----------------------------------
    # Range ring (redraw now and then)
    # ----------------------------------
    if now - last_ring_time >= RING_DELAY:
        API.DisplayRange(ENGAGE_RANGE, HUE_DANGER if danger else HUE_GOOD)
        last_ring_time = now
    API.Pause(LOOP_DELAY)
API.SysMsg("Lone Wolf offline", HUE_PARAGON)