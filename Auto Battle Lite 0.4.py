import API
import time


# ==========================================================
# Aegis Lite
#
# - Single main GUI only
# - Pause + Debug on main GUI
# - Target Mode button on main GUI
# - Pet 1 / Pet 2 / Reset on main GUI
# - Feeding toggle + Feed Mode + Lone Wolf on main GUI
# - Locked target retention once a target is acquired
# - Survival: Auto Res, Cure Poison, Emergency Heal,
#   Normal Heal, Greater Heal Potion
# - Combat: Auto Attack, Primary Ability, Secondary Ability
# - Utility: Potions, Grab Corpses
# - Visuals: Range Ring only
# - Lone Wolf disables pet support but still self-feeds
# - Default SPELL_GAP = 0.40
# ==========================================================


# ----------------------------------------------------------
# User tuning
# ----------------------------------------------------------


SCAN_RANGE = 12
ENGAGE_RANGE = 10
CHECK_DELAY = 0.10
DORMANT_DELAY = 5


HEAL_PERCENT = 85
CRITICAL_PERCENT = 45
PET_HEAL_PERCENT = 80


CURE_SPELL = "Cleanse by Fire"
HEAL_SPELL = "Greater Heal"


DEFAULT_SPELL_GAP = 0.40


FEED_DELAY = 30
POTION_DELAY = 600
POTION_GAP = 5
RING_DELAY = 3
GRAB_DELAY = 10


GREATER_HEAL_POTION_AT = 35
GREATER_HEAL_POTION_DELAY = 30
GREATER_HEAL_POTION_GRAPHIC = 0x0F0C
GREATER_HEAL_POTION_HUE = 0


UI_REFRESH_IDLE = 0.35
UI_REFRESH_ACTIVE = 0.18


# ----------------------------------------------------------
# UI colors and gump geometry
# ----------------------------------------------------------


HUE_INFO = 88
HUE_GOOD = 68
HUE_WARN = 53
HUE_DANGER = 33
HUE_PARAGON = 1150


GUMP_X = 100
GUMP_Y = 100
GUMP_W = 430
GUMP_H = 242


# ----------------------------------------------------------
# Persistent var keys
# ----------------------------------------------------------


VAR_PET1 = "aegis_lite_pet1"
VAR_PET2 = "aegis_lite_pet2"
VAR_LAST_POTION = "aegis_lite_last_potion"


VAR_FEED_MODE = "aegis_lite_feed_mode"
VAR_LONE_WOLF = "aegis_lite_lone_wolf"
VAR_DEBUG_MODE = "aegis_lite_debug_mode"
VAR_TARGET_MODE = "aegis_lite_target_mode"


VAR_USE_AUTO_RES = "aegis_lite_use_auto_res"
VAR_USE_CURE_POISON = "aegis_lite_use_cure_poison"
VAR_USE_EMERGENCY_HEAL = "aegis_lite_use_emergency_heal"
VAR_USE_NORMAL_HEAL = "aegis_lite_use_normal_heal"
VAR_USE_GREATER_HEAL_POTION = "aegis_lite_use_greater_heal_potion"


VAR_USE_PET_CURE = "aegis_lite_use_pet_cure"
VAR_USE_PET_HEAL = "aegis_lite_use_pet_heal"
VAR_USE_FEEDING = "aegis_lite_use_feeding"


VAR_USE_AUTO_ATTACK = "aegis_lite_use_auto_attack"
VAR_USE_PRIMARY_ABILITY = "aegis_lite_use_primary_ability"
VAR_USE_SECONDARY_ABILITY = "aegis_lite_use_secondary_ability"


VAR_USE_POTIONS = "aegis_lite_use_potions"
VAR_USE_GRAB_CORPSES = "aegis_lite_use_grab_corpses"
VAR_USE_RANGE_RING = "aegis_lite_use_range_ring"


# ----------------------------------------------------------
# Modes
# ----------------------------------------------------------


TARGET_SMART = 0
TARGET_CLOSEST = 1
DEFAULT_TARGET_MODE = TARGET_SMART


DEFAULT_FEED_MODE = 0
DEFAULT_LONE_WOLF = False


# ----------------------------------------------------------
# Defaults
# ----------------------------------------------------------


DEFAULTS = {
    "use_auto_res": True,
    "use_cure_poison": True,
    "use_emergency_heal": True,
    "use_normal_heal": True,
    "use_greater_heal_potion": False,


    "use_pet_cure": True,
    "use_pet_heal": True,
    "use_feeding": True,


    "use_auto_attack": True,
    "use_primary_ability": False,
    "use_secondary_ability": True,


    "use_potions": True,
    "use_grab_corpses": True,
    "use_range_ring": True,


    "debug_mode": False,
}


# ----------------------------------------------------------
# Toggle state
# ----------------------------------------------------------


use_auto_res = DEFAULTS["use_auto_res"]
use_cure_poison = DEFAULTS["use_cure_poison"]
use_emergency_heal = DEFAULTS["use_emergency_heal"]
use_normal_heal = DEFAULTS["use_normal_heal"]
use_greater_heal_potion = DEFAULTS["use_greater_heal_potion"]


use_pet_cure = DEFAULTS["use_pet_cure"]
use_pet_heal = DEFAULTS["use_pet_heal"]
use_feeding = DEFAULTS["use_feeding"]


use_auto_attack = DEFAULTS["use_auto_attack"]
use_primary_ability = DEFAULTS["use_primary_ability"]
use_secondary_ability = DEFAULTS["use_secondary_ability"]


use_potions = DEFAULTS["use_potions"]
use_grab_corpses = DEFAULTS["use_grab_corpses"]
use_range_ring = DEFAULTS["use_range_ring"]


debug_mode = DEFAULTS["debug_mode"]
target_mode = DEFAULT_TARGET_MODE
feed_mode = DEFAULT_FEED_MODE
lone_wolf = DEFAULT_LONE_WOLF


# ----------------------------------------------------------
# Runtime state
# ----------------------------------------------------------


last_feed_time = 0
last_potion_time = 0
last_ring_time = 0
last_grab_time = 0
last_greater_heal_potion_time = 0
last_spell_attempt_time = 0


current_target_serial = 0
last_hostile_time = time.time()


was_dead = False
dormant = False
paused = False
activity = ""


pet1_serial = 0
pet2_serial = 0
next_pet_to_feed = 1


pending_pet_set = 0
pending_pet_clear = False


status_gump = None
status_label = None
hp_label = None
hp_bar = None
target_label = None
mode_label = None
pet1_label = None
pet2_label = None
feed_label = None


status_pause_btn = None
status_debug_btn = None
status_target_mode_btn = None
status_lone_wolf_btn = None
status_feeding_btn = None
status_feed_mode_btn = None


last_ui_refresh_time = 0
last_ui_activity = ""
last_ui_target_serial = 0
last_ui_hp_bucket = -1
last_ui_paused = None
last_ui_dead = None


# ----------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------


def hp_percent():
    if API.Player.HitsMax <= 0:
        return 100
    return (API.Player.Hits * 100.0) / API.Player.HitsMax


def mobile_hp_percent(mobile):
    if not mobile:
        return 100
    if not hasattr(mobile, "HitsMax"):
        return 100
    if not hasattr(mobile, "Hits"):
        return 100
    if mobile.HitsMax is None or mobile.HitsMax <= 0:
        return 100
    return (mobile.Hits * 100.0) / mobile.HitsMax


def on_off(value):
    return "ON" if value else "OFF"


def bool_to_str(value):
    return "1" if value else "0"


def load_bool(key, default_value):
    raw = API.GetPersistentVar(key, "1" if default_value else "0", API.PersistentVar.Char)
    return raw == "1"


def save_bool(key, value):
    API.SavePersistentVar(key, bool_to_str(value), API.PersistentVar.Char)


def target_mode_name(mode_value):
    if mode_value == TARGET_CLOSEST:
        return "Closest"
    return "Smart"


def feed_mode_name(mode_value):
    modes = ["Round Robin", "Pet 1", "Pet 2", "None"]
    if mode_value < 0 or mode_value >= len(modes):
        return modes[0]
    return modes[mode_value]


def debug_msg(text, hue=HUE_INFO):
    if debug_mode:
        API.SysMsg("[Aegis DBG] " + text, hue)


def pet_desc(serial):
    if not serial:
        return "not set"
    m = API.FindMobile(serial)
    if m and m.Name:
        return m.Name
    return "0x%X" % serial


def gump_pos(g, default_x, default_y):
    for ax, ay in [("X", "Y"), ("ScreenCoordinateX", "ScreenCoordinateY"), ("LocX", "LocY")]:
        if hasattr(g, ax) and hasattr(g, ay):
            return getattr(g, ax), getattr(g, ay)

    if hasattr(g, "Location"):
        loc = g.Location
        if hasattr(loc, "X") and hasattr(loc, "Y"):
            return loc.X, loc.Y

    return default_x, default_y


def current_hp_bucket():
    return int(hp_percent() / 5)


def effective_spell_gap():
    return DEFAULT_SPELL_GAP


def set_activity(text, now, force=True):
    global activity
    activity = text
    maybe_refresh_status(now, force=force)


def is_valid_mobile(mobile):
    return mobile and not mobile.IsDead


def can_do_negative_act(mobile):
    if not is_valid_mobile(mobile):
        return False
    if mobile.Notoriety == API.Notoriety.Enemy:
        return True
    if mobile.Notoriety == API.Notoriety.Murderer:
        return True
    if mobile.Notoriety == API.Notoriety.Gray:
        return True
    if mobile.Notoriety == API.Notoriety.Criminal:
        return True
    return False


def is_valid_pet_serial(serial):
    if not serial:
        return False
    pet = API.FindMobile(serial)
    return pet and not pet.IsDead


# ----------------------------------------------------------
# Casting helpers
# ----------------------------------------------------------


def can_cast_spell(now):
    if now - last_spell_attempt_time < effective_spell_gap():
        debug_msg("Spell blocked by SPELL_GAP", HUE_WARN)
        return False

    if API.IsGlobalCooldownActive():
        debug_msg("Spell blocked by global cooldown", HUE_WARN)
        return False

    if API.InJournal("You are already casting a spell"):
        API.ClearJournal()
        debug_msg("Spell blocked by already-casting journal message", HUE_WARN)
        return False

    return True


def mark_spell_attempt(now):
    global last_spell_attempt_time
    last_spell_attempt_time = now


def cast_spell_if_ready(spell_name, now):
    if not can_cast_spell(now):
        return False
    API.CastSpell(spell_name)
    mark_spell_attempt(now)
    debug_msg("CastSpell: " + spell_name)
    return True


def wait_and_target_self():
    API.WaitForTarget()
    if API.HasTarget():
        API.TargetSelf()
        return True

    debug_msg("TargetSelf failed - no target cursor", HUE_WARN)
    API.CancelTarget()
    return False


def cast_spell_on_self(spell_name, now):
    if not cast_spell_if_ready(spell_name, now):
        return False
    if wait_and_target_self():
        API.Pause(CHECK_DELAY)
        return True
    return False


def cast_spell_on_mobile(spell_name, serial, now, hostile_only=False):
    if not cast_spell_if_ready(spell_name, now):
        return False

    API.WaitForTarget()

    if not API.HasTarget():
        debug_msg(spell_name + " failed - no target cursor", HUE_WARN)
        API.CancelTarget()
        return False

    mobile = API.FindMobile(serial)
    if not mobile or mobile.IsDead:
        debug_msg(spell_name + " failed - target invalid or dead", HUE_WARN)
        API.CancelTarget()
        return False

    if hostile_only and not can_do_negative_act(mobile):
        debug_msg(spell_name + " failed - target no longer hostile", HUE_WARN)
        API.CancelTarget()
        return False

    API.Target(serial)
    return True


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------


def load_settings():
    global last_potion_time, feed_mode, lone_wolf, debug_mode, target_mode
    global use_auto_res, use_cure_poison, use_emergency_heal, use_normal_heal
    global use_greater_heal_potion
    global use_pet_cure, use_pet_heal, use_feeding
    global use_auto_attack, use_primary_ability, use_secondary_ability
    global use_potions, use_grab_corpses, use_range_ring

    try:
        last_potion_time = float(API.GetPersistentVar(VAR_LAST_POTION, "0", API.PersistentVar.Char))
    except:
        last_potion_time = 0

    try:
        feed_mode = int(API.GetPersistentVar(VAR_FEED_MODE, str(DEFAULT_FEED_MODE), API.PersistentVar.Char))
    except:
        feed_mode = DEFAULT_FEED_MODE
    if feed_mode not in [0, 1, 2, 3]:
        feed_mode = DEFAULT_FEED_MODE

    lone_wolf = (API.GetPersistentVar(VAR_LONE_WOLF, "1" if DEFAULT_LONE_WOLF else "0", API.PersistentVar.Char) == "1")
    debug_mode = (API.GetPersistentVar(VAR_DEBUG_MODE, "0", API.PersistentVar.Char) == "1")

    try:
        target_mode = int(API.GetPersistentVar(VAR_TARGET_MODE, str(DEFAULT_TARGET_MODE), API.PersistentVar.Char))
    except:
        target_mode = DEFAULT_TARGET_MODE
    if target_mode not in [TARGET_SMART, TARGET_CLOSEST]:
        target_mode = DEFAULT_TARGET_MODE

    use_auto_res = load_bool(VAR_USE_AUTO_RES, DEFAULTS["use_auto_res"])
    use_cure_poison = load_bool(VAR_USE_CURE_POISON, DEFAULTS["use_cure_poison"])
    use_emergency_heal = load_bool(VAR_USE_EMERGENCY_HEAL, DEFAULTS["use_emergency_heal"])
    use_normal_heal = load_bool(VAR_USE_NORMAL_HEAL, DEFAULTS["use_normal_heal"])
    use_greater_heal_potion = load_bool(VAR_USE_GREATER_HEAL_POTION, DEFAULTS["use_greater_heal_potion"])

    use_pet_cure = load_bool(VAR_USE_PET_CURE, DEFAULTS["use_pet_cure"])
    use_pet_heal = load_bool(VAR_USE_PET_HEAL, DEFAULTS["use_pet_heal"])
    use_feeding = load_bool(VAR_USE_FEEDING, DEFAULTS["use_feeding"])

    use_auto_attack = load_bool(VAR_USE_AUTO_ATTACK, DEFAULTS["use_auto_attack"])
    use_primary_ability = load_bool(VAR_USE_PRIMARY_ABILITY, DEFAULTS["use_primary_ability"])
    use_secondary_ability = load_bool(VAR_USE_SECONDARY_ABILITY, DEFAULTS["use_secondary_ability"])

    use_potions = load_bool(VAR_USE_POTIONS, DEFAULTS["use_potions"])
    use_grab_corpses = load_bool(VAR_USE_GRAB_CORPSES, DEFAULTS["use_grab_corpses"])
    use_range_ring = load_bool(VAR_USE_RANGE_RING, DEFAULTS["use_range_ring"])


def save_settings():
    API.SavePersistentVar(VAR_LAST_POTION, str(last_potion_time), API.PersistentVar.Char)

    API.SavePersistentVar(VAR_FEED_MODE, str(feed_mode), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_LONE_WOLF, bool_to_str(lone_wolf), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_DEBUG_MODE, bool_to_str(debug_mode), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_TARGET_MODE, str(target_mode), API.PersistentVar.Char)

    save_bool(VAR_USE_AUTO_RES, use_auto_res)
    save_bool(VAR_USE_CURE_POISON, use_cure_poison)
    save_bool(VAR_USE_EMERGENCY_HEAL, use_emergency_heal)
    save_bool(VAR_USE_NORMAL_HEAL, use_normal_heal)
    save_bool(VAR_USE_GREATER_HEAL_POTION, use_greater_heal_potion)

    save_bool(VAR_USE_PET_CURE, use_pet_cure)
    save_bool(VAR_USE_PET_HEAL, use_pet_heal)
    save_bool(VAR_USE_FEEDING, use_feeding)

    save_bool(VAR_USE_AUTO_ATTACK, use_auto_attack)
    save_bool(VAR_USE_PRIMARY_ABILITY, use_primary_ability)
    save_bool(VAR_USE_SECONDARY_ABILITY, use_secondary_ability)

    save_bool(VAR_USE_POTIONS, use_potions)
    save_bool(VAR_USE_GRAB_CORPSES, use_grab_corpses)
    save_bool(VAR_USE_RANGE_RING, use_range_ring)


def load_pets():
    global pet1_serial, pet2_serial
    try:
        pet1_serial = int(API.GetPersistentVar(VAR_PET1, "0", API.PersistentVar.Char))
    except:
        pet1_serial = 0
    try:
        pet2_serial = int(API.GetPersistentVar(VAR_PET2, "0", API.PersistentVar.Char))
    except:
        pet2_serial = 0


def save_pets():
    API.SavePersistentVar(VAR_PET1, str(pet1_serial), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_PET2, str(pet2_serial), API.PersistentVar.Char)


# ----------------------------------------------------------
# GUI callbacks
# ----------------------------------------------------------


def toggle_pause():
    global paused
    paused = not paused
    API.SysMsg("Aegis paused" if paused else "Aegis resumed", HUE_WARN if paused else HUE_GOOD)
    maybe_refresh_status(time.time(), force=True)


def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    save_settings()
    refresh_status_gump()
    API.SysMsg("Aegis debug " + ("enabled" if debug_mode else "disabled"), HUE_INFO)


def cycle_target_mode():
    global target_mode
    target_mode = TARGET_CLOSEST if target_mode == TARGET_SMART else TARGET_SMART
    save_settings()
    maybe_refresh_status(time.time(), force=True)
    API.SysMsg("Target Mode: " + target_mode_name(target_mode), HUE_INFO)


def toggle_lone_wolf():
    global lone_wolf
    lone_wolf = not lone_wolf
    save_settings()
    maybe_refresh_status(time.time(), force=True)
    API.SysMsg("Lone Wolf " + ("enabled" if lone_wolf else "disabled"), HUE_INFO)


def toggle_feeding():
    global use_feeding
    use_feeding = not use_feeding
    save_settings()
    maybe_refresh_status(time.time(), force=True)
    API.SysMsg("Feeding " + ("enabled" if use_feeding else "disabled"), HUE_INFO)


def cycle_feed_mode():
    global feed_mode
    feed_mode = (feed_mode + 1) % 4
    save_settings()
    maybe_refresh_status(time.time(), force=True)
    API.SysMsg("Feed Mode: " + feed_mode_name(feed_mode), HUE_INFO)


def request_set_pet1():
    global pending_pet_set
    pending_pet_set = 1
    API.SysMsg("Target Pet 1", HUE_INFO)


def request_set_pet2():
    global pending_pet_set
    pending_pet_set = 2
    API.SysMsg("Target Pet 2", HUE_INFO)


def request_clear_pets():
    global pending_pet_clear
    pending_pet_clear = True


# ----------------------------------------------------------
# GUI
# ----------------------------------------------------------


def build_status_gump():
    global status_gump, status_label, hp_label, hp_bar, target_label, mode_label
    global pet1_label, pet2_label, feed_label
    global status_pause_btn, status_debug_btn, status_target_mode_btn
    global status_lone_wolf_btn, status_feeding_btn, status_feed_mode_btn
    global GUMP_X, GUMP_Y

    if status_gump and not status_gump.IsDisposed:
        GUMP_X, GUMP_Y = gump_pos(status_gump, GUMP_X, GUMP_Y)
        status_gump.Dispose()

    status_gump = API.CreateGump(True, True)
    status_gump.SetRect(GUMP_X, GUMP_Y, GUMP_W, GUMP_H)

    bg = API.CreateGumpColorBox(0.80, "#000000")
    bg.SetRect(0, 0, GUMP_W, GUMP_H)
    status_gump.Add(bg)

    title = API.CreateGumpLabel("Aegis Lite", HUE_PARAGON)
    title.SetPos(10, 6)
    status_gump.Add(title)

    status_pause_btn = API.CreateSimpleButton("Play" if paused else "Pause", 55, 18)
    status_pause_btn.SetPos(95, 5)
    API.AddControlOnClick(status_pause_btn, toggle_pause)
    status_gump.Add(status_pause_btn)

    status_debug_btn = API.CreateSimpleButton("Debug OFF", 78, 18)
    status_debug_btn.SetPos(155, 5)
    API.AddControlOnClick(status_debug_btn, toggle_debug_mode)
    status_gump.Add(status_debug_btn)

    status_target_mode_btn = API.CreateSimpleButton(target_mode_name(target_mode), 70, 18)
    status_target_mode_btn.SetPos(238, 5)
    API.AddControlOnClick(status_target_mode_btn, cycle_target_mode)
    status_gump.Add(status_target_mode_btn)

    status_lone_wolf_btn = API.CreateSimpleButton("Lone Wolf OFF", 105, 18)
    status_lone_wolf_btn.SetPos(313, 5)
    API.AddControlOnClick(status_lone_wolf_btn, toggle_lone_wolf)
    status_gump.Add(status_lone_wolf_btn)

    mode_label = API.CreateGumpLabel("Target: - | Lone Wolf: - | Debug: -", HUE_INFO)
    mode_label.SetPos(10, 28)
    status_gump.Add(mode_label)

    status_label = API.CreateGumpLabel("Status: starting", HUE_INFO)
    status_label.SetPos(10, 48)
    status_gump.Add(status_label)

    hp_label = API.CreateGumpLabel("HP: -", HUE_GOOD)
    hp_label.SetPos(10, 68)
    status_gump.Add(hp_label)

    hp_bar = API.CreateGumpSimpleProgressBar(250, 12, "#202020", "#20C020", 100, 100)
    hp_bar.SetPos(10, 88)
    status_gump.Add(hp_bar)

    target_label = API.CreateGumpLabel("Target: none", HUE_INFO)
    target_label.SetPos(10, 108)
    status_gump.Add(target_label)

    pet1_label = API.CreateGumpLabel("Pet 1: " + pet_desc(pet1_serial), HUE_INFO)
    pet1_label.SetPos(10, 132)
    status_gump.Add(pet1_label)

    pet1_btn = API.CreateSimpleButton("Set", 40, 18)
    pet1_btn.SetPos(210, 130)
    API.AddControlOnClick(pet1_btn, request_set_pet1)
    status_gump.Add(pet1_btn)

    pet2_label = API.CreateGumpLabel("Pet 2: " + pet_desc(pet2_serial), HUE_INFO)
    pet2_label.SetPos(10, 154)
    status_gump.Add(pet2_label)

    pet2_btn = API.CreateSimpleButton("Set", 40, 18)
    pet2_btn.SetPos(210, 152)
    API.AddControlOnClick(pet2_btn, request_set_pet2)
    status_gump.Add(pet2_btn)

    reset_btn = API.CreateSimpleButton("Reset Pets", 75, 18)
    reset_btn.SetPos(10, 178)
    API.AddControlOnClick(reset_btn, request_clear_pets)
    status_gump.Add(reset_btn)

    status_feeding_btn = API.CreateSimpleButton("Feed ON", 60, 18)
    status_feeding_btn.SetPos(95, 178)
    API.AddControlOnClick(status_feeding_btn, toggle_feeding)
    status_gump.Add(status_feeding_btn)

    status_feed_mode_btn = API.CreateSimpleButton("Mode", 50, 18)
    status_feed_mode_btn.SetPos(160, 178)
    API.AddControlOnClick(status_feed_mode_btn, cycle_feed_mode)
    status_gump.Add(status_feed_mode_btn)

    feed_label = API.CreateGumpLabel("Feed Mode: " + feed_mode_name(feed_mode), HUE_INFO)
    feed_label.SetPos(215, 180)
    status_gump.Add(feed_label)

    help_label = API.CreateGumpLabel("Lone Wolf disables pet support but still self-feeds.", HUE_WARN)
    help_label.SetPos(10, 202)
    status_gump.Add(help_label)

    API.AddGump(status_gump)
    maybe_refresh_status(time.time(), force=True)


def refresh_status_gump():
    if not status_gump or status_gump.IsDisposed:
        return

    if status_pause_btn:
        status_pause_btn.Text = "Play" if paused else "Pause"

    if status_debug_btn:
        status_debug_btn.Text = "Debug " + on_off(debug_mode)

    if status_target_mode_btn:
        status_target_mode_btn.Text = target_mode_name(target_mode)

    if status_lone_wolf_btn:
        status_lone_wolf_btn.Text = "Lone Wolf " + on_off(lone_wolf)

    if status_feeding_btn:
        status_feeding_btn.Text = "Feed " + on_off(use_feeding)

    if mode_label:
        mode_label.Text = "Target: %s | Lone Wolf: %s | Debug: %s" % (
            target_mode_name(target_mode),
            on_off(lone_wolf),
            on_off(debug_mode)
        )

    if paused:
        status_label.Text = "Status: PAUSED"
    elif API.Player.IsDead:
        status_label.Text = "Status: DEAD"
    elif activity:
        status_label.Text = "Status: " + activity
    elif dormant:
        status_label.Text = "Status: dormant"
    elif current_target_serial:
        status_label.Text = "Status: fighting"
    else:
        status_label.Text = "Status: idle"

    hp_label.Text = "HP: %d / %d (%d%%)" % (
        API.Player.Hits,
        API.Player.HitsMax,
        int(hp_percent())
    )

    hp_bar.SetProgress(API.Player.Hits, max(API.Player.HitsMax, 1))

    tgt = None
    if current_target_serial:
        tgt = API.FindMobile(current_target_serial)

    if tgt and not tgt.IsDead:
        name = tgt.Name if tgt.Name else "?"
        if len(name) > 24:
            name = name[:24]
        try:
            pct = int(mobile_hp_percent(tgt))
            target_label.Text = "Target: %s %d%%" % (name, pct)
        except:
            target_label.Text = "Target: %s ??%%" % name
    else:
        target_label.Text = "Target: none"

    if pet1_label:
        pet1_label.Text = "Pet 1: " + pet_desc(pet1_serial)

    if pet2_label:
        pet2_label.Text = "Pet 2: " + pet_desc(pet2_serial)

    if feed_label:
        feed_label.Text = "Feed Mode: " + feed_mode_name(feed_mode)


def maybe_refresh_status(now, force=False):
    global last_ui_refresh_time, last_ui_activity, last_ui_target_serial
    global last_ui_hp_bucket, last_ui_paused, last_ui_dead

    hp_bucket = current_hp_bucket()
    dead_now = API.Player.IsDead

    changed = (
        force
        or activity != last_ui_activity
        or current_target_serial != last_ui_target_serial
        or hp_bucket != last_ui_hp_bucket
        or paused != last_ui_paused
        or dead_now != last_ui_dead
    )

    interval = UI_REFRESH_ACTIVE if (current_target_serial or activity) else UI_REFRESH_IDLE

    if not changed and (now - last_ui_refresh_time) < interval:
        return

    refresh_status_gump()
    last_ui_refresh_time = now
    last_ui_activity = activity
    last_ui_target_serial = current_target_serial
    last_ui_hp_bucket = hp_bucket
    last_ui_paused = paused
    last_ui_dead = dead_now


# ----------------------------------------------------------
# GUI actions needing target/state mutation
# ----------------------------------------------------------


def handle_gui_actions():
    global pending_pet_set, pending_pet_clear
    global pet1_serial, pet2_serial

    if pending_pet_clear:
        pending_pet_clear = False
        pet1_serial = 0
        pet2_serial = 0
        save_pets()
        API.SysMsg("Pets reset", HUE_WARN)
        maybe_refresh_status(time.time(), force=True)

    if pending_pet_set:
        slot = pending_pet_set
        pending_pet_set = 0

        serial = API.RequestTarget(timeout=10)
        if serial:
            if slot == 1:
                pet1_serial = serial
            else:
                pet2_serial = serial
            save_pets()
            API.SysMsg("Pet %d saved" % slot, HUE_GOOD)
        else:
            API.SysMsg("Cancelled", HUE_WARN)

        maybe_refresh_status(time.time(), force=True)


# ----------------------------------------------------------
# Hostile selection
# ----------------------------------------------------------


def choose_enemy_from_hostiles(hostiles):
    elite_paragon = None
    elite_only = None
    paragon_only = None
    nearest_other = None
    nearest_any = None
    danger = False

    for m in hostiles:
        if not is_valid_mobile(m):
            continue

        if not nearest_any or m.Distance < nearest_any.Distance:
            nearest_any = m

        nm = m.Name.lower() if m.Name else ""
        is_para = "paragon" in nm
        is_elite = "elite" in nm

        if m.Distance <= 4 and (
            m.Notoriety == API.Notoriety.Murderer
            or m.Notoriety == API.Notoriety.Enemy
            or is_para
        ):
            danger = True

        if target_mode == TARGET_CLOSEST:
            continue

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

    if target_mode == TARGET_CLOSEST:
        return nearest_any, danger

    return elite_paragon or elite_only or paragon_only or nearest_other, danger


# ----------------------------------------------------------
# Pet helpers
# ----------------------------------------------------------


def get_pet_support_need():
    if lone_wolf:
        return (None, 0)

    for pet_serial in [pet1_serial, pet2_serial]:
        pet = API.FindMobile(pet_serial)
        if not pet or pet.IsDead:
            continue

        if use_pet_cure and pet.IsPoisoned:
            return ("cure", pet_serial)

        if use_pet_heal and mobile_hp_percent(pet) <= PET_HEAL_PERCENT:
            return ("heal", pet_serial)

    return (None, 0)


def perform_pet_support(pet_need, pet_serial, now):
    if pet_need == "cure":
        if cast_spell_on_mobile(CURE_SPELL, pet_serial, now, hostile_only=False):
            set_activity("curing pet", now)
            return True

    if pet_need == "heal":
        if cast_spell_on_mobile(HEAL_SPELL, pet_serial, now, hostile_only=False):
            set_activity("healing pet", now)
            return True

    return False


def feed_pet_command(command, pet_serial):
    API.Msg(command)
    API.WaitForTarget()

    if API.HasTarget():
        API.Target(pet_serial)
        return True

    debug_msg(command + " failed - no target cursor", HUE_WARN)
    API.CancelTarget()
    return False


def choose_pet_to_feed():
    global next_pet_to_feed

    pet_serial = 0

    if feed_mode == 0:
        pet_serial = pet1_serial if next_pet_to_feed == 1 else pet2_serial
        next_pet_to_feed = 2 if next_pet_to_feed == 1 else 1
    elif feed_mode == 1:
        pet_serial = pet1_serial
    elif feed_mode == 2:
        pet_serial = pet2_serial

    return pet_serial


# ----------------------------------------------------------
# Hotkeys
# ----------------------------------------------------------


def hotkey_toggle_pause():
    toggle_pause()


API.OnHotKey("CTRL+SHIFT+P", hotkey_toggle_pause)


# ----------------------------------------------------------
# Startup
# ----------------------------------------------------------


API.SysMsg("Aegis Lite online", HUE_PARAGON)
load_pets()
load_settings()
build_status_gump()

API.SysMsg("Target Mode: " + target_mode_name(target_mode), HUE_INFO)
API.SysMsg("SPELL_GAP fixed at %.2f" % DEFAULT_SPELL_GAP, HUE_INFO)

if not pet1_serial and not pet2_serial:
    API.SysMsg("No pets set - use the main GUI if needed", HUE_INFO)


# ----------------------------------------------------------
# Main loop
# ----------------------------------------------------------


while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    handle_gui_actions()

    activity = ""
    maybe_refresh_status(now)

    if paused:
        API.Pause(CHECK_DELAY)
        continue

    if API.Player.IsDead:
        if use_auto_res:
            set_activity("awaiting res", now)
            if not was_dead:
                API.SysMsg("Died - trying to res", HUE_DANGER)
                was_dead = True
            API.Msg("[res")
            API.Pause(2.0)
            current_target_serial = 0
        else:
            activity = "dead"

        maybe_refresh_status(now, force=True)
        API.Pause(CHECK_DELAY)
        continue

    if was_dead:
        API.SysMsg("Back up", HUE_GOOD)
        API.Msg("all guard me")
        API.Pause(0.25)
        API.SetWarMode(True)
        was_dead = False

    player_hp = hp_percent()
    player_poisoned = API.Player.IsPoisoned

    # Highest priority self survival
    if use_cure_poison and player_poisoned:
        set_activity("curing poison", now)
        if cast_spell_on_self(CURE_SPELL, now):
            continue

    if use_emergency_heal and player_hp <= CRITICAL_PERCENT:
        set_activity("EMERGENCY HEAL", now)
        if cast_spell_on_self(HEAL_SPELL, now):
            continue

    # Pet support only when not in Lone Wolf
    pet_need, urgent_pet_serial = get_pet_support_need()
    pet_busy = (pet_need is not None)

    if pet_busy and perform_pet_support(pet_need, urgent_pet_serial, now):
        continue

    if use_normal_heal and player_hp <= HEAL_PERCENT:
        set_activity("healing self", now)
        if cast_spell_on_self(HEAL_SPELL, now):
            continue

    if use_greater_heal_potion and player_hp <= GREATER_HEAL_POTION_AT and now - last_greater_heal_potion_time >= GREATER_HEAL_POTION_DELAY:
        set_activity("greater heal potion", now)
        API.UseType(GREATER_HEAL_POTION_GRAPHIC, GREATER_HEAL_POTION_HUE)
        API.Pause(CHECK_DELAY)
        last_greater_heal_potion_time = now
        continue

    hostiles = API.NearestMobiles(
        [
            API.Notoriety.Gray,
            API.Notoriety.Criminal,
            API.Notoriety.Enemy,
            API.Notoriety.Murderer
        ],
        SCAN_RANGE
    )

    if hostiles:
        last_hostile_time = now
        if dormant:
            API.SysMsg("Hostile detected - waking up", HUE_GOOD)
            dormant = False
    else:
        if now - last_hostile_time >= DORMANT_DELAY:
            if not dormant:
                API.SysMsg("Entering dormant mode", HUE_INFO)
                dormant = True
            maybe_refresh_status(now, force=True)
            API.Pause(CHECK_DELAY)
            continue

    enemy = None
    danger = False

    locked_enemy = None
    if current_target_serial:
        locked_enemy = API.FindMobile(current_target_serial)
        if locked_enemy:
            if (
                not is_valid_mobile(locked_enemy)
                or not can_do_negative_act(locked_enemy)
                or locked_enemy.Distance > SCAN_RANGE
            ):
                current_target_serial = 0
                locked_enemy = None
        else:
            current_target_serial = 0

    if locked_enemy:
        enemy = locked_enemy

        nm = locked_enemy.Name.lower() if locked_enemy.Name else ""
        is_para = "paragon" in nm
        if locked_enemy.Distance <= 4 and (
            locked_enemy.Notoriety == API.Notoriety.Murderer
            or locked_enemy.Notoriety == API.Notoriety.Enemy
            or is_para
        ):
            danger = True
    else:
        if hostiles:
            chosen_enemy, danger = choose_enemy_from_hostiles(hostiles)
            if chosen_enemy:
                enemy = chosen_enemy
                current_target_serial = chosen_enemy.Serial
            else:
                current_target_serial = 0
        else:
            current_target_serial = 0

    if enemy and use_auto_attack:
        API.Attack(enemy.Serial)

    if enemy and can_do_negative_act(enemy):
        if use_primary_ability and not API.PrimaryAbilityActive():
            API.ToggleAbility("primary")
        if use_secondary_ability and not API.SecondaryAbilityActive():
            API.ToggleAbility("secondary")

    if use_grab_corpses and now - last_grab_time >= GRAB_DELAY:
        corpse = API.NearestCorpse(2)
        if corpse:
            API.Msg("[grab")
            last_grab_time = now

    if use_feeding and now - last_feed_time >= FEED_DELAY:
        set_activity("feeding", now)

        if lone_wolf:
            API.Msg("[feedps")
            API.Pause(CHECK_DELAY)
            API.Msg("[feedarti")
            API.Pause(CHECK_DELAY)
        else:
            pet_serial = choose_pet_to_feed()

            if pet_serial and is_valid_pet_serial(pet_serial):
                feed_pet_command("[feedps", pet_serial)
                feed_pet_command("[feedarti", pet_serial)
            elif feed_mode != 3:
                debug_msg("Feeding skipped - chosen pet missing or invalid", HUE_WARN)

        API.CreateCooldownBar(FEED_DELAY, "Feeding", HUE_INFO)
        last_feed_time = now
        continue

    if use_potions and now - last_potion_time >= POTION_DELAY:
        set_activity("potions", now)

        API.SysMsg("Using Star Potion", HUE_INFO)
        API.UseType(0x0F09, 2902)
        API.Pause(POTION_GAP)

        API.SysMsg("Using Potion of Greed", HUE_INFO)
        API.UseType(0x0F09, 2910)

        API.CreateCooldownBar(POTION_DELAY, "Potions", HUE_INFO)
        last_potion_time = now
        save_settings()
        continue

    if use_range_ring and now - last_ring_time >= RING_DELAY:
        API.DisplayRange(ENGAGE_RANGE, HUE_DANGER if danger else HUE_GOOD)
        last_ring_time = now

    maybe_refresh_status(now)
    API.Pause(CHECK_DELAY)


# ----------------------------------------------------------
# Shutdown
# ----------------------------------------------------------


API.OnHotKey("CTRL+SHIFT+P")

if status_gump and not status_gump.IsDisposed:
    status_gump.Dispose()

API.SysMsg("Aegis Lite offline", HUE_PARAGON)