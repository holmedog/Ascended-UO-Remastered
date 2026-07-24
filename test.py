import API
import time


# ==========================================================
# Aegis - Guardian + Threat Radar
#
# Priority / responsiveness version
# - Pet support moved to higher priority
# - Low-priority work suppressed while pets need support
# - Status gump refresh throttled to reduce loop churn
# - One-time Curse per target serial
# - Dedicated Remove Curse retry delay
# ==========================================================


# ----------------------------------------------------------
# User tuning: combat ranges, delays, thresholds
# ----------------------------------------------------------

SCAN_RANGE = 12
ENGAGE_RANGE = 10
CHECK_DELAY = 0.10
DORMANT_DELAY = 5

HEAL_PERCENT = 95
CRITICAL_PERCENT = 65
PET_HEAL_PERCENT = 90

CURE_SPELL = "Cleanse by Fire"
HEAL_SPELL = "Greater Heal"

BUFF_DELAY = 8
FIRE_FIELD_DELAY = 10
CURSE_WEAPON_DELAY = 12
FEED_DELAY = 30

HONOR_DELAY = 5.0
DISCORDANCE_DELAY = 8.0
CURSE_DELAY = 2.5
REMOVE_CURSE_DELAY = 2.5
ENEMY_OF_ONE_DELAY = 3.0
ENEMY_OF_ONE_DURATION = 120.0
ENEMY_OF_ONE_REFRESH_WINDOW = 12.0

SPELL_GAP = .4

POTION_DELAY = 600
POTION_GAP = 5

RING_DELAY = 3
GRAB_DELAY = 10

GREATER_HEAL_POTION_AT = 35
GREATER_HEAL_POTION_DELAY = 30
GREATER_HEAL_POTION_GRAPHIC = 0x0F0C
GREATER_HEAL_POTION_HUE = 0

UI_REFRESH_IDLE = 0.85
UI_REFRESH_ACTIVE = 0.3

last_loop_time = time.time()
last_slow_loop_time = 0


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
GUMP_W = 300
GUMP_H = 118

CONFIG_GUMP_W = 760
CONFIG_GUMP_MIN_H = 360
CONFIG_GUMP_BOTTOM_PAD = 24

LEFT_X = 16
RIGHT_X = 390
LABEL_OFFSET = 0
BUTTON_X_OFFSET = 150
ROW_H = 22
SECTION_GAP = 8

last_loop_time = 0

# ----------------------------------------------------------
# Persistent var keys
# ----------------------------------------------------------

VAR_PET1 = "aegis_pet1"
VAR_PET2 = "aegis_pet2"
VAR_LAST_POTION = "aegis_last_potion"

VAR_FEED_MODE = "aegis_feed_mode"
VAR_LONE_WOLF = "aegis_lone_wolf"
VAR_DEBUG_MODE = "aegis_debug_mode"

VAR_USE_AUTO_RES = "aegis_use_auto_res"
VAR_USE_CURE_POISON = "aegis_use_cure_poison"
VAR_USE_EMERGENCY_HEAL = "aegis_use_emergency_heal"
VAR_USE_NORMAL_HEAL = "aegis_use_normal_heal"
VAR_USE_GREATER_HEAL_POTION = "aegis_use_greater_heal_potion"
VAR_USE_REMOVE_CURSE = "aegis_use_remove_curse"

VAR_USE_PET_CURE = "aegis_use_pet_cure"
VAR_USE_PET_HEAL = "aegis_use_pet_heal"
VAR_USE_FEEDING = "aegis_use_feeding"

VAR_USE_HONOR = "aegis_use_honor"
VAR_USE_DISCORDANCE = "aegis_use_discordance"
VAR_USE_CURSE = "aegis_use_curse"
VAR_USE_ENEMY_OF_ONE = "aegis_use_enemy_of_one"

VAR_USE_AUTO_ATTACK = "aegis_use_auto_attack"
VAR_USE_PRIMARY_ABILITY = "aegis_use_primary_ability"
VAR_USE_SECONDARY_ABILITY = "aegis_use_secondary_ability"
VAR_USE_FIRE_FIELD = "aegis_use_fire_field"

VAR_USE_DIVINE_FURY = "aegis_use_divine_fury"
VAR_USE_IMMOLATING_WEAPON = "aegis_use_immolating_weapon"
VAR_USE_CONSECRATE_WEAPON = "aegis_use_consecrate_weapon"
VAR_USE_CURSE_WEAPON = "aegis_use_curse_weapon"

VAR_USE_POTIONS = "aegis_use_potions"
VAR_USE_GRAB_CORPSES = "aegis_use_grab_corpses"

VAR_USE_RANGE_RING = "aegis_use_range_ring"
VAR_USE_HOSTILE_OUTLINES = "aegis_use_hostile_outlines"
VAR_USE_PARAGON_MARKERS = "aegis_use_paragon_markers"


# ----------------------------------------------------------
# Defaults
# ----------------------------------------------------------

DEFAULTS = {
    "use_auto_res": True,
    "use_cure_poison": True,
    "use_emergency_heal": True,
    "use_normal_heal": True,
    "use_greater_heal_potion": False,
    "use_remove_curse": True,

    "use_pet_cure": True,
    "use_pet_heal": True,
    "use_feeding": True,

    "use_honor": True,
    "use_discordance": True,
    "use_curse": True,
    "use_enemy_of_one": True,

    "use_auto_attack": True,
    "use_primary_ability": False,
    "use_secondary_ABILITY": True,
    "use_fire_field": True,

    "use_divine_fury": True,
    "use_immolating_weapon": True,
    "use_consecrate_weapon": True,
    "use_curse_weapon": True,

    "use_potions": True,
    "use_grab_corpses": True,

    "use_range_ring": True,
    "use_hostile_outlines": True,
    "use_paragon_markers": True,

    "debug_mode": False,
}

DEFAULT_FEED_MODE = 0
DEFAULT_LONE_WOLF = False


# ----------------------------------------------------------
# Toggle state
# ----------------------------------------------------------

use_auto_res = DEFAULTS["use_auto_res"]
use_cure_poison = DEFAULTS["use_cure_poison"]
use_emergency_heal = DEFAULTS["use_emergency_heal"]
use_normal_heal = DEFAULTS["use_normal_heal"]
use_greater_heal_potion = DEFAULTS["use_greater_heal_potion"]
use_remove_curse = DEFAULTS["use_remove_curse"]

use_pet_cure = DEFAULTS["use_pet_cure"]
use_pet_heal = DEFAULTS["use_pet_heal"]
use_feeding = DEFAULTS["use_feeding"]

use_honor = DEFAULTS["use_honor"]
use_discordance = DEFAULTS["use_discordance"]
use_curse = DEFAULTS["use_curse"]
use_enemy_of_one = DEFAULTS["use_enemy_of_one"]

use_auto_attack = DEFAULTS["use_auto_res"] and True
use_primary_ability = DEFAULTS["use_primary_ability"]
use_secondary_ability = True
use_fire_field = DEFAULTS["use_fire_field"]

use_divine_fury = DEFAULTS["use_divine_fury"]
use_immolating_weapon = DEFAULTS["use_immolating_weapon"]
use_consecrate_weapon = DEFAULTS["use_consecrate_weapon"]
use_curse_weapon = DEFAULTS["use_curse_weapon"]

use_potions = DEFAULTS["use_potions"]
use_grab_corpses = DEFAULTS["use_grab_corpses"]

use_range_ring = DEFAULTS["use_range_ring"]
use_hostile_outlines = DEFAULTS["use_hostile_outlines"]
use_paragon_markers = DEFAULTS["use_paragon_markers"]

debug_mode = DEFAULTS["debug_mode"]


# ----------------------------------------------------------
# Runtime state
# ----------------------------------------------------------

feed_mode = DEFAULT_FEED_MODE
lone_wolf = DEFAULT_LONE_WOLF

last_buff_time = 0
last_fire_field_time = 0
last_curse_weapon_time = 0
last_feed_time = 0
last_potion_time = 0
last_ring_time = 0
last_grab_time = 0
last_greater_heal_potion_time = 0

last_honor_time = 0
last_discordance_time = 0
last_curse_time = 0
last_remove_curse_time = 0
last_enemy_of_one_time = 0
last_enemy_of_one_cast_time = 0
last_spell_attempt_time = 0

current_target_serial = 0
last_honor_target_serial = 0
last_curse_target_serial = 0
last_discordance_target_serial = 0
last_enemy_of_one_target_serial = 0
last_hostile_time = time.time()

seen_paragons = []

was_dead = False
dormant = False
paused = False
activity = ""

pet1_serial = 0
pet2_serial = 0
next_pet_to_feed = 1

pending_pet_set = 0
pending_pet_clear = False
pending_reset_defaults = False

status_gump = None
status_label = None
hp_label = None
hp_bar = None
target_label = None
status_pause_btn = None

config_gump = None
config_bg = None
config_toggle_buttons = {}
config_feed_label = None
config_pet1_label = None
config_pet2_label = None
config_lone_wolf_button = None
config_debug_button = None
config_visible = False

last_ui_refresh_time = 0
last_ui_activity = ""
last_ui_target_serial = 0
last_ui_hp_bucket = -1
last_ui_paused = None
last_ui_dead = None

timer_start = 0.0
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


def debug_msg(text, hue=HUE_INFO):
    if debug_mode:
        API.SysMsg("[Aegis DBG] " + text, hue)


def pet_desc(serial):
    if not serial:
        return "not set"
    m = API.FindMobile(serial)
    if m and m.Name:
        return m.Name
    return "0x%X (not nearby)" % serial


def gump_pos(g, default_x, default_y):
    for ax, ay in [("X", "Y"), ("ScreenCoordinateX", "ScreenCoordinateY"), ("LocX", "LocY")]:
        if hasattr(g, ax) and hasattr(g, ay):
            return getattr(g, ax), getattr(g, ay)

    if hasattr(g, "Location"):
        loc = g.Location
        if hasattr(loc, "X") and hasattr(loc, "Y"):
            return loc.X, loc.Y

    return default_x, default_y


def set_label_text(control, text):
    if control:
        control.Text = text


def set_button_text(control, text):
    if control:
        control.Text = text


def get_feed_mode_text():
    modes = ["Round Robin", "Pet 1", "Pet 2", "None"]
    return "Feed Mode: " + modes[feed_mode]


def current_hp_bucket():
    return int(hp_percent() / 5)


# ----------------------------------------------------------
# Validation helpers
# ----------------------------------------------------------

def is_valid_mobile(mobile):
    return mobile and not mobile.IsDead


def can_do_negative_act(mobile):
    if not is_valid_mobile(mobile):
        return False
    if mobile.Notoriety == API.Notoriety.Enemy:
        return True
    if mobile.Notoriety == API.Notoriety.Murderer:
        return True
    return False


def is_valid_pet_serial(serial):
    if not serial:
        return False
    pet = API.FindMobile(serial)
    return pet and not pet.IsDead


# ----------------------------------------------------------
# Casting / throttling helpers
# ----------------------------------------------------------

def report_cast_block(reason):
    debug_msg(reason, HUE_WARN)


def can_cast_spell(now):
    if now - last_spell_attempt_time < SPELL_GAP:
        report_cast_block("Spell blocked by SPELL_GAP")
        return False

    if API.IsGlobalCooldownActive():
        report_cast_block("Spell blocked by global cooldown")
        return False

    if API.InJournal("You are already casting a spell"):
        API.ClearJournal()
        report_cast_block("Spell blocked by already-casting journal message")
        return False

    return True


def mark_spell_attempt(now):
    global last_spell_attempt_time
    last_spell_attempt_time = now


def mark_nonspell_action(now):
    global last_spell_attempt_time
    last_spell_attempt_time = now


def cast_spell_if_ready(spell_name, now):
    if not can_cast_spell(now):
        return False
    API.CastSpell(spell_name)
    mark_spell_attempt(now)
    debug_msg("CastSpell: " + spell_name)
    return True


def can_use_honor(now):
    if now - last_spell_attempt_time < SPELL_GAP:
        return False
    if now - last_honor_time < HONOR_DELAY:
        return False
    return True


# ----------------------------------------------------------
# Shared target helpers
# ----------------------------------------------------------

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
    return wait_and_target_self()


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


def use_skill_on_mobile(skill_name, serial, now, hostile_only=False):
    API.UseSkill(skill_name)
    mark_nonspell_action(now)
    debug_msg("UseSkill: " + skill_name)
    API.WaitForTarget()

    if not API.HasTarget():
        debug_msg(skill_name + " failed - no target cursor", HUE_WARN)
        API.CancelTarget()
        return False

    mobile = API.FindMobile(serial)
    if not mobile or mobile.IsDead:
        debug_msg(skill_name + " failed - target invalid or dead", HUE_WARN)
        API.CancelTarget()
        return False

    if hostile_only and not can_do_negative_act(mobile):
        debug_msg(skill_name + " failed - target no longer hostile", HUE_WARN)
        API.CancelTarget()
        return False

    API.Target(serial)
    return True


def has_remove_curse_debuff():
    return (
        API.BuffExists("Weaken")
        or API.BuffExists("Clumsy")
        or API.BuffExists("Feeblemind")
        or API.BuffExists("Curse")
    )


def enemy_of_one_refresh_due(now, enemy):
    if not enemy:
        return False

    if not API.BuffExists("Enemy of One"):
        return True

    if now - last_enemy_of_one_cast_time >= ENEMY_OF_ONE_DURATION - ENEMY_OF_ONE_REFRESH_WINDOW:
        return True

    if last_enemy_of_one_target_serial and enemy.Serial != last_enemy_of_one_target_serial:
        return True

    return False


# ----------------------------------------------------------
# Pet urgency helpers
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
    global activity

    if pet_need == "cure":
        if cast_spell_on_mobile(CURE_SPELL, pet_serial, now, hostile_only=False):
            activity = "curing pet"
            maybe_refresh_status(now, force=True)
            return True

    if pet_need == "heal":
        if cast_spell_on_mobile(HEAL_SPELL, pet_serial, now, hostile_only=False):
            activity = "healing pet"
            maybe_refresh_status(now, force=True)
            return True

    return False


# ----------------------------------------------------------
# Reset helpers
# ----------------------------------------------------------

def apply_recommended_defaults():
    global feed_mode, lone_wolf, debug_mode
    global use_auto_res, use_cure_poison, use_emergency_heal, use_normal_heal
    global use_greater_heal_potion, use_remove_curse
    global use_pet_cure, use_pet_heal, use_feeding
    global use_honor, use_discordance, use_curse, use_enemy_of_one
    global use_auto_attack, use_primary_ability, use_secondary_ability, use_fire_field
    global use_divine_fury, use_immolating_weapon, use_consecrate_weapon, use_curse_weapon
    global use_potions, use_grab_corpses
    global use_range_ring, use_hostile_outlines, use_paragon_markers

    use_auto_res = DEFAULTS["use_auto_res"]
    use_cure_poison = DEFAULTS["use_cure_poison"]
    use_emergency_heal = DEFAULTS["use_emergency_heal"]
    use_normal_heal = DEFAULTS["use_normal_heal"]
    use_greater_heal_potion = DEFAULTS["use_greater_heal_potion"]
    use_remove_curse = DEFAULTS["use_remove_curse"]

    use_pet_cure = DEFAULTS["use_pet_cure"]
    use_pet_heal = DEFAULTS["use_pet_heal"]
    use_feeding = DEFAULTS["use_feeding"]

    use_honor = DEFAULTS["use_honor"]
    use_discordance = DEFAULTS["use_discordance"]
    use_curse = DEFAULTS["use_curse"]
    use_enemy_of_one = DEFAULTS["use_enemy_of_one"]

    use_auto_attack = DEFAULTS["use_auto_attack"]
    use_primary_ability = DEFAULTS["use_primary_ability"]
    use_secondary_ability = True
    use_fire_field = DEFAULTS["use_fire_field"]

    use_divine_fury = DEFAULTS["use_divine_fury"]
    use_immolating_weapon = DEFAULTS["use_immolating_weapon"]
    use_consecrate_weapon = DEFAULTS["use_consecrate_weapon"]
    use_curse_weapon = DEFAULTS["use_curse_weapon"]

    use_potions = DEFAULTS["use_potions"]
    use_grab_corpses = DEFAULTS["use_grab_corpses"]

    use_range_ring = DEFAULTS["use_range_ring"]
    use_hostile_outlines = DEFAULTS["use_hostile_outlines"]
    use_paragon_markers = DEFAULTS["use_paragon_markers"]

    feed_mode = DEFAULT_FEED_MODE
    lone_wolf = DEFAULT_LONE_WOLF
    debug_mode = DEFAULTS["debug_mode"]

    save_settings()


# ----------------------------------------------------------
# Config metadata
# ----------------------------------------------------------

def left_column_specs():
    return [
        ("Combat Opener", [
            ("Honor", "use_honor", toggle_use_honor),
            ("Discordance", "use_discordance", toggle_use_discordance),
            ("Curse", "use_curse", toggle_use_curse),
            ("Enemy of One", "use_enemy_of_one", toggle_use_enemy_of_one),
        ]),
        ("Combat Loop", [
            ("Auto Attack", "use_auto_attack", toggle_use_auto_attack),
            ("Primary Ability", "use_primary_ability", toggle_use_primary_ability),
            ("Secondary Ability", "use_secondary_ability", toggle_use_secondary_ability),
            ("Fire Field", "use_fire_field", toggle_use_fire_field),
        ]),
        ("Survival", [
            ("Auto Res", "use_auto_res", toggle_use_auto_res),
            ("Cure Poison", "use_cure_poison", toggle_use_cure_poison),
            ("Emergency Heal", "use_emergency_heal", toggle_use_emergency_heal),
            ("Normal Heal", "use_normal_heal", toggle_use_normal_heal),
            ("Greater Heal Potion", "use_greater_heal_potion", toggle_use_greater_heal_potion),
            ("Remove Curse", "use_remove_curse", toggle_use_remove_curse),
        ]),
        ("Buffs", [
            ("Divine Fury", "use_divine_fury", toggle_use_divine_fury),
            ("Immolating Weapon", "use_immolating_weapon", toggle_use_immolating_weapon),
            ("Consecrate Weapon", "use_consecrate_weapon", toggle_use_consecrate_weapon),
            ("Curse Weapon", "use_curse_weapon", toggle_use_curse_weapon),
        ]),
    ]


def all_toggle_specs():
    rows = []
    for section, items in left_column_specs():
        for label, var_name, callback in items:
            rows.append((section, label, var_name, callback))

    for label, var_name, callback in [
        ("Pet Cure", "use_pet_cure", toggle_use_pet_cure),
        ("Pet Heal", "use_pet_heal", toggle_use_pet_heal),
        ("Feeding", "use_feeding", toggle_use_feeding),
        ("Potions", "use_potions", toggle_use_potions),
        ("Grab Corpses", "use_grab_corpses", toggle_use_grab_corpses),
        ("Range Ring", "use_range_ring", toggle_use_range_ring),
        ("Hostile Outlines", "use_hostile_outlines", toggle_use_hostile_outlines),
        ("Paragon Markers", "use_paragon_markers", toggle_use_paragon_markers),
    ]:
        rows.append(("Right", label, var_name, callback))

    return rows


# ----------------------------------------------------------
# Persistence
# ----------------------------------------------------------

def load_settings():
    global last_potion_time, feed_mode, lone_wolf, debug_mode
    global use_auto_res, use_cure_poison, use_emergency_heal, use_normal_heal
    global use_greater_heal_potion, use_remove_curse
    global use_pet_cure, use_pet_heal, use_feeding
    global use_honor, use_discordance, use_curse, use_enemy_of_one
    global use_auto_attack, use_primary_ability, use_secondary_ability, use_fire_field
    global use_divine_fury, use_immolating_weapon, use_consecrate_weapon, use_curse_weapon
    global use_potions, use_grab_corpses
    global use_range_ring, use_hostile_outlines, use_paragon_markers

    last_potion_time = float(API.GetPersistentVar(VAR_LAST_POTION, "0", API.PersistentVar.Char))

    feed_mode = int(API.GetPersistentVar(VAR_FEED_MODE, str(DEFAULT_FEED_MODE), API.PersistentVar.Char))
    lone_wolf = (API.GetPersistentVar(VAR_LONE_WOLF, "1" if DEFAULT_LONE_WOLF else "0", API.PersistentVar.Char) == "1")
    debug_mode = (API.GetPersistentVar(VAR_DEBUG_MODE, "0", API.PersistentVar.Char) == "1")

    use_auto_res = load_bool(VAR_USE_AUTO_RES, DEFAULTS["use_auto_res"])
    use_cure_poison = load_bool(VAR_USE_CURE_POISON, DEFAULTS["use_cure_poison"])
    use_emergency_heal = load_bool(VAR_USE_EMERGENCY_HEAL, DEFAULTS["use_emergency_heal"])
    use_normal_heal = load_bool(VAR_USE_NORMAL_HEAL, DEFAULTS["use_normal_heal"])
    use_greater_heal_potion = load_bool(VAR_USE_GREATER_HEAL_POTION, DEFAULTS["use_greater_heal_potion"])
    use_remove_curse = load_bool(VAR_USE_REMOVE_CURSE, DEFAULTS["use_remove_curse"])

    use_pet_cure = load_bool(VAR_USE_PET_CURE, DEFAULTS["use_pet_cure"])
    use_pet_heal = load_bool(VAR_USE_PET_HEAL, DEFAULTS["use_pet_heal"])
    use_feeding = load_bool(VAR_USE_FEEDING, DEFAULTS["use_feeding"])

    use_honor = load_bool(VAR_USE_HONOR, DEFAULTS["use_honor"])
    use_discordance = load_bool(VAR_USE_DISCORDANCE, DEFAULTS["use_discordance"])
    use_curse = load_bool(VAR_USE_CURSE, DEFAULTS["use_curse"])
    use_enemy_of_one = load_bool(VAR_USE_ENEMY_OF_ONE, DEFAULTS["use_enemy_of_one"])

    use_auto_attack = load_bool(VAR_USE_AUTO_ATTACK, DEFAULTS["use_auto_attack"])
    use_primary_ability = load_bool(VAR_USE_PRIMARY_ABILITY, DEFAULTS["use_primary_ability"])
    use_secondary_ability = load_bool(VAR_USE_SECONDARY_ABILITY, True)
    use_fire_field = load_bool(VAR_USE_FIRE_FIELD, DEFAULTS["use_fire_field"])

    use_divine_fury = load_bool(VAR_USE_DIVINE_FURY, DEFAULTS["use_divine_fury"])
    use_immolating_weapon = load_bool(VAR_USE_IMMOLATING_WEAPON, DEFAULTS["use_immolating_weapon"])
    use_consecrate_weapon = load_bool(VAR_USE_CONSECRATE_WEAPON, DEFAULTS["use_consecrate_weapon"])
    use_curse_weapon = load_bool(VAR_USE_CURSE_WEAPON, DEFAULTS["use_curse_weapon"])

    use_potions = load_bool(VAR_USE_POTIONS, DEFAULTS["use_potions"])
    use_grab_corpses = load_bool(VAR_USE_GRAB_CORPSES, DEFAULTS["use_grab_corpses"])

    use_range_ring = load_bool(VAR_USE_RANGE_RING, DEFAULTS["use_range_ring"])
    use_hostile_outlines = load_bool(VAR_USE_HOSTILE_OUTLINES, DEFAULTS["use_hostile_outlines"])
    use_paragon_markers = load_bool(VAR_USE_PARAGON_MARKERS, DEFAULTS["use_paragon_markers"])


def save_settings():
    API.SavePersistentVar(VAR_LAST_POTION, str(last_potion_time), API.PersistentVar.Char)

    API.SavePersistentVar(VAR_FEED_MODE, str(feed_mode), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_LONE_WOLF, bool_to_str(lone_wolf), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_DEBUG_MODE, bool_to_str(debug_mode), API.PersistentVar.Char)

    save_bool(VAR_USE_AUTO_RES, use_auto_res)
    save_bool(VAR_USE_CURE_POISON, use_cure_poison)
    save_bool(VAR_USE_EMERGENCY_HEAL, use_emergency_heal)
    save_bool(VAR_USE_NORMAL_HEAL, use_normal_heal)
    save_bool(VAR_USE_GREATER_HEAL_POTION, use_greater_heal_potion)
    save_bool(VAR_USE_REMOVE_CURSE, use_remove_curse)

    save_bool(VAR_USE_PET_CURE, use_pet_cure)
    save_bool(VAR_USE_PET_HEAL, use_pet_heal)
    save_bool(VAR_USE_FEEDING, use_feeding)

    save_bool(VAR_USE_HONOR, use_honor)
    save_bool(VAR_USE_DISCORDANCE, use_discordance)
    save_bool(VAR_USE_CURSE, use_curse)
    save_bool(VAR_USE_ENEMY_OF_ONE, use_enemy_of_one)

    save_bool(VAR_USE_AUTO_ATTACK, use_auto_attack)
    save_bool(VAR_USE_PRIMARY_ABILITY, use_primary_ability)
    save_bool(VAR_USE_SECONDARY_ABILITY, use_secondary_ability)
    save_bool(VAR_USE_FIRE_FIELD, use_fire_field)

    save_bool(VAR_USE_DIVINE_FURY, use_divine_fury)
    save_bool(VAR_USE_IMMOLATING_WEAPON, use_immolating_weapon)
    save_bool(VAR_USE_CONSECRATE_WEAPON, use_consecrate_weapon)
    save_bool(VAR_USE_CURSE_WEAPON, use_curse_weapon)

    save_bool(VAR_USE_POTIONS, use_potions)
    save_bool(VAR_USE_GRAB_CORPSES, use_grab_corpses)

    save_bool(VAR_USE_RANGE_RING, use_range_ring)
    save_bool(VAR_USE_HOSTILE_OUTLINES, use_hostile_outlines)
    save_bool(VAR_USE_PARAGON_MARKERS, use_paragon_markers)


def load_pets():
    global pet1_serial, pet2_serial
    pet1_serial = int(API.GetPersistentVar(VAR_PET1, "0", API.PersistentVar.Char))
    pet2_serial = int(API.GetPersistentVar(VAR_PET2, "0", API.PersistentVar.Char))


def save_pets():
    API.SavePersistentVar(VAR_PET1, str(pet1_serial), API.PersistentVar.Char)
    API.SavePersistentVar(VAR_PET2, str(pet2_serial), API.PersistentVar.Char)


# ----------------------------------------------------------
# Toggle mutation
# ----------------------------------------------------------

def flip_toggle(var_name):
    globals()[var_name] = not globals()[var_name]
    save_settings()
    refresh_config_controls()


def toggle_use_auto_res():
    flip_toggle("use_auto_res")

def toggle_use_cure_poison():
    flip_toggle("use_cure_poison")

def toggle_use_emergency_heal():
    flip_toggle("use_emergency_heal")

def toggle_use_normal_heal():
    flip_toggle("use_normal_heal")

def toggle_use_greater_heal_potion():
    flip_toggle("use_greater_heal_potion")

def toggle_use_remove_curse():
    flip_toggle("use_remove_curse")

def toggle_use_pet_cure():
    flip_toggle("use_pet_cure")

def toggle_use_pet_heal():
    flip_toggle("use_pet_heal")

def toggle_use_feeding():
    flip_toggle("use_feeding")

def toggle_use_honor():
    flip_toggle("use_honor")

def toggle_use_discordance():
    flip_toggle("use_discordance")

def toggle_use_curse():
    flip_toggle("use_curse")

def toggle_use_enemy_of_one():
    flip_toggle("use_enemy_of_one")

def toggle_use_auto_attack():
    flip_toggle("use_auto_attack")

def toggle_use_primary_ability():
    flip_toggle("use_primary_ability")

def toggle_use_secondary_ability():
    flip_toggle("use_secondary_ability")

def toggle_use_fire_field():
    flip_toggle("use_fire_field")

def toggle_use_divine_fury():
    flip_toggle("use_divine_fury")

def toggle_use_immolating_weapon():
    flip_toggle("use_immolating_weapon")

def toggle_use_consecrate_weapon():
    flip_toggle("use_consecrate_weapon")

def toggle_use_curse_weapon():
    flip_toggle("use_curse_weapon")

def toggle_use_potions():
    flip_toggle("use_potions")

def toggle_use_grab_corpses():
    flip_toggle("use_grab_corpses")

def toggle_use_range_ring():
    flip_toggle("use_range_ring")

def toggle_use_hostile_outlines():
    flip_toggle("use_hostile_outlines")

def toggle_use_paragon_markers():
    flip_toggle("use_paragon_markers")


# ----------------------------------------------------------
# Other callbacks
# ----------------------------------------------------------

def toggle_pause():
    global paused
    paused = not paused
    API.SysMsg("Aegis paused" if paused else "Aegis resumed", HUE_WARN if paused else HUE_GOOD)
    maybe_refresh_status(time.time(), force=True)


def cycle_feed_mode():
    global feed_mode
    feed_mode = (feed_mode + 1) % 4
    save_settings()
    refresh_config_controls()


def toggle_lone_wolf():
    global lone_wolf
    lone_wolf = not lone_wolf
    save_settings()
    refresh_config_controls()


def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    save_settings()
    refresh_config_controls()
    API.SysMsg("Aegis debug " + ("enabled" if debug_mode else "disabled"), HUE_INFO)


def request_set_pet1():
    global pending_pet_set
    pending_pet_set = 1


def request_set_pet2():
    global pending_pet_set
    pending_pet_set = 2


def request_clear_pets():
    global pending_pet_clear
    pending_pet_clear = True


def request_reset_defaults():
    global pending_reset_defaults
    pending_reset_defaults = True


def open_config():
    global config_visible
    config_visible = True
    if not config_gump or config_gump.IsDisposed:
        build_config_gump()
    else:
        refresh_config_controls()


def close_config():
    global config_gump, config_visible
    config_visible = False
    if config_gump and not config_gump.IsDisposed:
        config_gump.Dispose()
    config_gump = None


# ----------------------------------------------------------
# Hotkeys
# ----------------------------------------------------------

def hotkey_toggle_pause():
    toggle_pause()

def hotkey_open_config():
    open_config()

API.OnHotKey("CTRL+SHIFT+P", hotkey_toggle_pause)
API.OnHotKey("CTRL+SHIFT+O", hotkey_open_config)


# ----------------------------------------------------------
# Status gump
# ----------------------------------------------------------

def build_status_gump():
    global status_gump, status_label, hp_label, hp_bar, target_label, status_pause_btn
    global GUMP_X, GUMP_Y

    if status_gump and not status_gump.IsDisposed:
        GUMP_X, GUMP_Y = gump_pos(status_gump, GUMP_X, GUMP_Y)
        status_gump.Dispose()

    status_gump = API.CreateGump(True, True)
    status_gump.SetRect(GUMP_X, GUMP_Y, GUMP_W, GUMP_H)

    bg = API.CreateGumpColorBox(0.75, "#000000")
    bg.SetRect(0, 0, GUMP_W, GUMP_H)
    status_gump.Add(bg)

    title = API.CreateGumpLabel("Aegis", HUE_PARAGON)
    title.SetPos(10, 6)
    status_gump.Add(title)

    status_pause_btn = API.CreateSimpleButton("Play" if paused else "Pause", 55, 18)
    status_pause_btn.SetPos(95, 5)
    API.AddControlOnClick(status_pause_btn, toggle_pause)
    status_gump.Add(status_pause_btn)

    config_btn = API.CreateSimpleButton("Config", 55, 18)
    config_btn.SetPos(160, 5)
    API.AddControlOnClick(config_btn, open_config)
    status_gump.Add(config_btn)

    status_label = API.CreateGumpLabel("Status: starting", HUE_INFO)
    status_label.SetPos(10, 30)
    status_gump.Add(status_label)

    hp_label = API.CreateGumpLabel("HP: -", HUE_GOOD)
    hp_label.SetPos(10, 50)
    status_gump.Add(hp_label)

    hp_bar = API.CreateGumpSimpleProgressBar(210, 12, "#202020", "#20C020", 100, 100)
    hp_bar.SetPos(10, 70)
    status_gump.Add(hp_bar)

    target_label = API.CreateGumpLabel("Target: none", HUE_INFO)
    target_label.SetPos(10, 90)
    status_gump.Add(target_label)

    API.AddGump(status_gump)
    maybe_refresh_status(time.time(), force=True)


def refresh_status_gump():
    if not status_gump or status_gump.IsDisposed:
        return

    if status_pause_btn:
        status_pause_btn.Text = "Play" if paused else "Pause"

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
        if len(name) > 22:
            name = name[:22]

        pct = 100
        try:
            pct = int(mobile_hp_percent(tgt))
        except:
            pct = 100

        target_label.Text = "Target: %s %d%%" % (name, pct)
    else:
        target_label.Text = "Target: none"


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
# Config gump
# ----------------------------------------------------------

def add_toggle_row(gump, base_x, y, label_text, value, callback, key_name):
    lbl = API.CreateGumpLabel(label_text, HUE_INFO)
    lbl.SetPos(base_x + LABEL_OFFSET, y)
    gump.Add(lbl)

    btn = API.CreateSimpleButton(on_off(value), 55, 18)
    btn.SetPos(base_x + BUTTON_X_OFFSET, y - 2)
    API.AddControlOnClick(btn, callback)
    gump.Add(btn)

    config_toggle_buttons[key_name] = btn


def add_section_header(gump, base_x, y, text):
    hdr = API.CreateGumpLabel(text, HUE_PARAGON)
    hdr.SetPos(base_x, y)
    gump.Add(hdr)


def add_hint(gump, x, y, text):
    lbl = API.CreateGumpLabel(text, HUE_WARN)
    lbl.SetPos(x, y)
    gump.Add(lbl)


def build_left_column(gump, start_y):
    y = start_y

    for section, items in left_column_specs():
        add_section_header(gump, LEFT_X, y, section)
        y += ROW_H

        for label, var_name, callback in items:
            add_toggle_row(gump, LEFT_X + 6, y, label, globals()[var_name], callback, var_name)
            y += ROW_H

        y += SECTION_GAP

    return y


def build_right_column(gump, start_y):
    global config_pet1_label, config_pet2_label, config_feed_label
    global config_lone_wolf_button, config_debug_button

    y = start_y

    add_section_header(gump, RIGHT_X, y, "Pets")
    y += ROW_H

    for label, var_name, callback in [
        ("Pet Cure", "use_pet_cure", toggle_use_pet_cure),
        ("Pet Heal", "use_pet_heal", toggle_use_pet_heal),
        ("Feeding", "use_feeding", toggle_use_feeding),
    ]:
        add_toggle_row(gump, RIGHT_X + 6, y, label, globals()[var_name], callback, var_name)
        y += ROW_H

    config_pet1_label = API.CreateGumpLabel("Pet 1: " + pet_desc(pet1_serial), HUE_INFO)
    config_pet1_label.SetPos(RIGHT_X + 6, y)
    gump.Add(config_pet1_label)

    set1 = API.CreateSimpleButton("Set", 45, 18)
    set1.SetPos(RIGHT_X + BUTTON_X_OFFSET + 6, y - 2)
    API.AddControlOnClick(set1, request_set_pet1)
    gump.Add(set1)
    y += ROW_H

    config_pet2_label = API.CreateGumpLabel("Pet 2: " + pet_desc(pet2_serial), HUE_INFO)
    config_pet2_label.SetPos(RIGHT_X + 6, y)
    gump.Add(config_pet2_label)

    set2 = API.CreateSimpleButton("Set", 45, 18)
    set2.SetPos(RIGHT_X + BUTTON_X_OFFSET + 6, y - 2)
    API.AddControlOnClick(set2, request_set_pet2)
    gump.Add(set2)
    y += ROW_H

    clr = API.CreateSimpleButton("Reset Both", 80, 18)
    clr.SetPos(RIGHT_X + 6, y - 2)
    API.AddControlOnClick(clr, request_clear_pets)
    gump.Add(clr)
    y += 28

    add_hint(gump, RIGHT_X + 6, y, "Set pets once, then pet healing/cures target them automatically.")
    y += 18 + SECTION_GAP

    add_section_header(gump, RIGHT_X, y, "Utility")
    y += ROW_H
    add_toggle_row(gump, RIGHT_X + 6, y, "Potions", use_potions, toggle_use_potions, "use_potions")
    y += ROW_H
    add_toggle_row(gump, RIGHT_X + 6, y, "Grab Corpses", use_grab_corpses, toggle_use_grab_corpses, "use_grab_corpses")
    y += ROW_H + SECTION_GAP

    add_section_header(gump, RIGHT_X, y, "Visuals")
    y += ROW_H
    add_toggle_row(gump, RIGHT_X + 6, y, "Range Ring", use_range_ring, toggle_use_range_ring, "use_range_ring")
    y += ROW_H
    add_toggle_row(gump, RIGHT_X + 6, y, "Hostile Outlines", use_hostile_outlines, toggle_use_hostile_outlines, "use_hostile_outlines")
    y += ROW_H
    add_toggle_row(gump, RIGHT_X + 6, y, "Paragon Markers", use_paragon_markers, toggle_use_paragon_markers, "use_paragon_markers")
    y += ROW_H + SECTION_GAP

    add_section_header(gump, RIGHT_X, y, "Modes")
    y += ROW_H

    lone_lbl = API.CreateGumpLabel("Lone Wolf", HUE_INFO)
    lone_lbl.SetPos(RIGHT_X + 6, y)
    gump.Add(lone_lbl)

    config_lone_wolf_button = API.CreateSimpleButton(on_off(lone_wolf), 55, 18)
    config_lone_wolf_button.SetPos(RIGHT_X + BUTTON_X_OFFSET + 6, y - 2)
    API.AddControlOnClick(config_lone_wolf_button, toggle_lone_wolf)
    gump.Add(config_lone_wolf_button)
    y += ROW_H

    add_hint(gump, RIGHT_X + 6, y, "Lone Wolf skips pet support and uses self-feeding only.")
    y += 18

    config_feed_label = API.CreateGumpLabel(get_feed_mode_text(), HUE_INFO)
    config_feed_label.SetPos(RIGHT_X + 6, y)
    gump.Add(config_feed_label)

    feed_btn = API.CreateSimpleButton("Change", 60, 18)
    feed_btn.SetPos(RIGHT_X + BUTTON_X_OFFSET + 1, y - 2)
    API.AddControlOnClick(feed_btn, cycle_feed_mode)
    gump.Add(feed_btn)
    y += ROW_H

    add_hint(gump, RIGHT_X + 6, y, "Round Robin alternates pets; None disables pet feeding.")
    y += 18

    dbg_lbl = API.CreateGumpLabel("Debug Mode", HUE_INFO)
    dbg_lbl.SetPos(RIGHT_X + 6, y)
    gump.Add(dbg_lbl)

    config_debug_button = API.CreateSimpleButton(on_off(debug_mode), 55, 18)
    config_debug_button.SetPos(RIGHT_X + BUTTON_X_OFFSET + 6, y - 2)
    API.AddControlOnClick(config_debug_button, toggle_debug_mode)
    gump.Add(config_debug_button)
    y += ROW_H

    add_hint(gump, RIGHT_X + 6, y, "Debug shows why actions were blocked or cancelled.")
    y += 18

    reset_btn = API.CreateSimpleButton("Reset Defaults", 110, 20)
    reset_btn.SetPos(RIGHT_X + 6, y)
    API.AddControlOnClick(reset_btn, request_reset_defaults)
    gump.Add(reset_btn)
    y += 28

    return y


def build_config_gump():
    global config_gump, config_bg, config_toggle_buttons
    global config_feed_label, config_pet1_label, config_pet2_label
    global config_lone_wolf_button, config_debug_button

    config_toggle_buttons = {}
    config_feed_label = None
    config_pet1_label = None
    config_pet2_label = None
    config_lone_wolf_button = None
    config_debug_button = None

    x = GUMP_X + GUMP_W + 10
    y0 = GUMP_Y

    if config_gump and not config_gump.IsDisposed:
        x, y0 = gump_pos(config_gump, x, y0)
        config_gump.Dispose()

    config_gump = API.CreateGump(True, True)
    config_gump.SetRect(x, y0, CONFIG_GUMP_W, CONFIG_GUMP_MIN_H)

    config_bg = API.CreateGumpColorBox(0.85, "#101018")
    config_bg.SetRect(0, 0, CONFIG_GUMP_W, CONFIG_GUMP_MIN_H)
    config_gump.Add(config_bg)

    title = API.CreateGumpLabel("Aegis Config", HUE_PARAGON)
    title.SetPos(10, 8)
    config_gump.Add(title)

    close_btn = API.CreateSimpleButton("Close", 55, 18)
    close_btn.SetPos(CONFIG_GUMP_W - 70, 6)
    API.AddControlOnClick(close_btn, close_config)
    config_gump.Add(close_btn)

    start_y = 34
    left_y = build_left_column(config_gump, start_y)
    right_y = build_right_column(config_gump, start_y)

    panel_height = max(CONFIG_GUMP_MIN_H, max(left_y, right_y) + CONFIG_GUMP_BOTTOM_PAD)
    config_gump.SetRect(x, y0, CONFIG_GUMP_W, panel_height)
    config_bg.SetRect(0, 0, CONFIG_GUMP_W, panel_height)

    API.AddGump(config_gump)
    refresh_config_controls()


def refresh_config_controls():
    if not config_gump or config_gump.IsDisposed:
        return

    for _, _, var_name, _ in all_toggle_specs():
        if var_name in config_toggle_buttons:
            set_button_text(config_toggle_buttons[var_name], on_off(globals()[var_name]))

    set_button_text(config_lone_wolf_button, on_off(lone_wolf))
    set_button_text(config_debug_button, on_off(debug_mode))
    set_label_text(config_feed_label, get_feed_mode_text())
    set_label_text(config_pet1_label, "Pet 1: " + pet_desc(pet1_serial))
    set_label_text(config_pet2_label, "Pet 2: " + pet_desc(pet2_serial))


# ----------------------------------------------------------
# Config actions needing target or state mutation
# ----------------------------------------------------------

def handle_config_actions():
    global pending_pet_set, pending_pet_clear, pending_reset_defaults
    global pet1_serial, pet2_serial

    if pending_pet_clear:
        pending_pet_clear = False
        pet1_serial = 0
        pet2_serial = 0
        save_pets()
        API.SysMsg("Companions reset", HUE_WARN)
        refresh_config_controls()

    if pending_reset_defaults:
        pending_reset_defaults = False
        apply_recommended_defaults()
        API.SysMsg("Aegis defaults restored", HUE_GOOD)
        refresh_config_controls()

    if pending_pet_set:
        slot = pending_pet_set
        pending_pet_set = 0

        API.SysMsg("Target companion #%d" % slot, HUE_INFO)
        serial = API.RequestTarget(timeout=10)

        if serial:
            if slot == 1:
                pet1_serial = serial
            else:
                pet2_serial = serial
            save_pets()
            API.SysMsg("Companion #%d saved" % slot, HUE_GOOD)
        else:
            API.SysMsg("Cancelled", HUE_WARN)

        refresh_config_controls()


# ----------------------------------------------------------
# Hostile selection
# ----------------------------------------------------------

def choose_enemy_from_hostiles(hostiles):
    elite_paragon = None
    elite_only = None
    paragon_only = None
    nearest_other = None
    danger = False

    for m in hostiles:
        if not is_valid_mobile(m):
            continue

        nm = m.Name.lower() if m.Name else ""
        is_para = "paragon" in nm
        is_elite = "elite" in nm

        if use_hostile_outlines:
            if m.Name and "Paragon" in m.Name:
                color = "#FF00FF"
            elif m.Notoriety == API.Notoriety.Murderer or m.Notoriety == API.Notoriety.Enemy:
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

        if m.Distance <= 4 and (m.Notoriety == API.Notoriety.Murderer or m.Notoriety == API.Notoriety.Enemy or is_para):
            danger = True

        if is_para and use_paragon_markers:
            if m.Serial not in seen_paragons:
                seen_paragons.append(m.Serial)
                API.SysMsg("PARAGON: " + m.Name, HUE_PARAGON)
                API.HeadMsg("PARAGON", m.Serial, HUE_PARAGON)
                API.AddMapMarker("Paragon: " + m.Name, m.X, m.Y, API.GetMap(), "purple")
                    
    
    return elite_paragon or elite_only or paragon_only or nearest_other, danger


# ----------------------------------------------------------
# Startup
# ----------------------------------------------------------

API.SysMsg("Aegis online", HUE_PARAGON)
load_pets()
load_settings()
build_status_gump()

if not pet1_serial and not pet2_serial:
    API.SysMsg("No companions set - open Config to add them", HUE_INFO)


# ----------------------------------------------------------
# Main loop
# ----------------------------------------------------------

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()
    
    # === LOOP TIMING MEASUREMENT ===
    current_loop_time = time.time()
    loop_duration_ms = (current_loop_time - last_loop_time) * 1000
    last_loop_time = current_loop_time

    if loop_duration_ms > 1200:
        time_since_last_slow = current_loop_time - last_slow_loop_time
        last_slow_loop_time = current_loop_time

        API.SysMsg(f"SLOW LOOP: {loop_duration_ms:.1f} ms  |  {time_since_last_slow:.1f}s since previous slow loop", HUE_PARAGON)
    # =================================

    if paused:
        API.Pause(CHECK_DELAY)
        continue

    # ------------------------------------------------------
    # Death / revive
    # ------------------------------------------------------

    if API.Player.IsDead:
        if use_auto_res:
            activity = "awaiting res"
            if not was_dead:
                API.SysMsg("Died - trying to res", HUE_DANGER)
                was_dead = True
            maybe_refresh_status(now, force=True)
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
        last_buff_time = 0
        last_fire_field_time = 0
        last_curse_weapon_time = 0
        was_dead = False

    # ------------------------------------------------------
    # Highest priority self-preservation
    # ------------------------------------------------------

    if use_cure_poison and API.Player.IsPoisoned:
        if cast_spell_on_self(CURE_SPELL, now):
            activity = "curing poison"
            maybe_refresh_status(now, force=True)
            continue

    if use_emergency_heal and hp_percent() <= CRITICAL_PERCENT:
        if cast_spell_on_self(HEAL_SPELL, now):
            activity = "EMERGENCY HEAL"
            maybe_refresh_status(now, force=True)
            continue

    # ------------------------------------------------------
    # High-priority companion support
    # ------------------------------------------------------

    pet_need, urgent_pet_serial = get_pet_support_need()
    pet_busy = (pet_need is not None)

    if pet_busy:
        if perform_pet_support(pet_need, urgent_pet_serial, now):
            API.Pause(CHECK_DELAY)
            continue

    # ------------------------------------------------------
    # Normal player sustain after urgent pet support
    # ------------------------------------------------------

    if use_normal_heal and hp_percent() <= HEAL_PERCENT:
        if cast_spell_on_self(HEAL_SPELL, now):
            activity = "healing self"
            maybe_refresh_status(now, force=True)
            continue

    if use_greater_heal_potion and hp_percent() <= GREATER_HEAL_POTION_AT and now - last_greater_heal_potion_time >= GREATER_HEAL_POTION_DELAY:
        activity = "greater heal potion"
        maybe_refresh_status(now, force=True)
        API.UseType(GREATER_HEAL_POTION_GRAPHIC, GREATER_HEAL_POTION_HUE)
        API.Pause(CHECK_DELAY)
        last_greater_heal_potion_time = now
        continue

    if use_remove_curse and not pet_busy and now - last_remove_curse_time >= REMOVE_CURSE_DELAY:
        if has_remove_curse_debuff():
            if cast_spell_on_self("Remove Curse", now):
                activity = "remove curse"
                maybe_refresh_status(now, force=True)
                API.CreateCooldownBar(REMOVE_CURSE_DELAY, "Remove Curse", HUE_INFO)
                last_remove_curse_time = now
                continue



    # ------------------------------------------------------
    # Config Stuff
    # ------------------------------------------------------

    handle_config_actions()

    if config_visible and (not config_gump or config_gump.IsDisposed):
        build_config_gump()

    activity = ""
    maybe_refresh_status(now)


    # ------------------------------------------------------
    # Hostile scan / dormant mode
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Maintain or replace current target
    # ------------------------------------------------------

    enemy = None
    danger = False

    if current_target_serial:
        enemy = API.FindMobile(current_target_serial)
        if not is_valid_mobile(enemy):
            current_target_serial = 0
            enemy = None

    if hostiles:
        chosen_enemy, danger = choose_enemy_from_hostiles(hostiles)
        if chosen_enemy:
            enemy = chosen_enemy

    if enemy:
        current_target_serial = enemy.Serial
    else:
        current_target_serial = 0

    # ------------------------------------------------------
    # Combat opener system
    # ------------------------------------------------------

    if enemy:
        if use_honor:
            if enemy.Serial != last_honor_target_serial and enemy.HitsDiff == 0 and can_use_honor(now):
                activity = "honor"
                maybe_refresh_status(now, force=True)
                API.Virtue("honor")
                mark_nonspell_action(now)
                API.WaitForTarget()

                if API.HasTarget():
                    API.Target(enemy)
                else:
                    debug_msg("Honor failed - no target cursor", HUE_WARN)
                    API.CancelTarget()

                API.Pause(CHECK_DELAY)
                API.CancelTarget()
                last_honor_time = now
                last_honor_target_serial = enemy.Serial
                continue

        if use_discordance and can_do_negative_act(enemy):
            if enemy.Serial != last_discordance_target_serial and now - last_discordance_time >= DISCORDANCE_DELAY:
                activity = "discordance"
                maybe_refresh_status(now, force=True)

                if use_skill_on_mobile("Discordance", enemy.Serial, now, hostile_only=True):
                    last_discordance_time = now
                    last_discordance_target_serial = enemy.Serial
                    continue

        if use_curse and can_do_negative_act(enemy):
            if enemy.Serial != last_curse_target_serial and now - last_curse_time >= CURSE_DELAY:
                activity = "curse"
                maybe_refresh_status(now, force=True)

                if cast_spell_on_mobile("Curse", enemy.Serial, now, hostile_only=True):
                    API.CreateCooldownBar(CURSE_DELAY, "Curse", HUE_INFO)
                    last_curse_target_serial = enemy.Serial
                    last_curse_time = now
                    continue

        if use_enemy_of_one and enemy_of_one_refresh_due(now, enemy):
            if now - last_enemy_of_one_time >= ENEMY_OF_ONE_DELAY:
                if cast_spell_if_ready("Enemy of One", now):
                    activity = "enemy of one"
                    maybe_refresh_status(now, force=True)
                    API.Pause(CHECK_DELAY)
                    API.CancelTarget()
                    last_enemy_of_one_time = now
                    last_enemy_of_one_cast_time = now
                    last_enemy_of_one_target_serial = enemy.Serial
                    continue

        if use_auto_attack:
            API.Attack(enemy.Serial)

    # ------------------------------------------------------
    # Combat loop
    # ------------------------------------------------------

    if enemy and can_do_negative_act(enemy):
        if use_primary_ability and not API.PrimaryAbilityActive():
            API.ToggleAbility("primary")
        if use_secondary_ability and not API.SecondaryAbilityActive():
            API.ToggleAbility("secondary")

    # ------------------------------------------------------
    # Lower priority work - skip while pet is urgent
    # ------------------------------------------------------

    if not pet_busy:
        if use_grab_corpses and now - last_grab_time >= GRAB_DELAY:
            corpse = API.NearestCorpse(2)
            if corpse:
                API.Msg("[grab")
                last_grab_time = now

        if use_divine_fury and not API.BuffExists("Divine Fury"):
            if cast_spell_if_ready("Divine Fury", now):
                API.Pause(CHECK_DELAY)

        if use_fire_field and now - last_fire_field_time >= FIRE_FIELD_DELAY and not API.Player.IsPoisoned and hp_percent() > HEAL_PERCENT:
            if cast_spell_if_ready("Fire Field", now):
                API.Pause(CHECK_DELAY)
                last_fire_field_time = now
                continue

        if use_curse_weapon and now - last_curse_weapon_time >= CURSE_WEAPON_DELAY and not API.Player.IsPoisoned and hp_percent() > HEAL_PERCENT:
            if cast_spell_if_ready("Curse Weapon", now):
                API.Pause(CHECK_DELAY)
                last_curse_weapon_time = now
                continue

        if now - last_buff_time >= BUFF_DELAY and not API.Player.IsPoisoned and hp_percent() > HEAL_PERCENT:
            buff_cast = False

            if use_immolating_weapon:
                if cast_spell_if_ready("Immolating Weapon", now):
                    API.Pause(CHECK_DELAY)
                    buff_cast = True
                    now = time.time()

            if use_consecrate_weapon:
                if cast_spell_if_ready("Consecrate Weapon", now):
                    API.Pause(CHECK_DELAY)
                    buff_cast = True

            if buff_cast:
                API.CreateCooldownBar(BUFF_DELAY, "Buffs", HUE_INFO)
                last_buff_time = time.time()
                continue

        if use_feeding and now - last_feed_time >= FEED_DELAY:
            if lone_wolf:
                API.Msg("[feedps")
                API.Pause(CHECK_DELAY)
                API.Msg("[feedarti")
                API.Pause(CHECK_DELAY)
            else:
                pet_serial = 0

                if feed_mode == 0:
                    pet_serial = pet1_serial if next_pet_to_feed == 1 else pet2_serial
                    next_pet_to_feed = 2 if next_pet_to_feed == 1 else 1
                elif feed_mode == 1:
                    pet_serial = pet1_serial
                elif feed_mode == 2:
                    pet_serial = pet2_serial

                if pet_serial and is_valid_pet_serial(pet_serial):
                    API.Msg("[feedps")
                    API.WaitForTarget()
                    if API.HasTarget():
                        API.Target(pet_serial)
                    else:
                        debug_msg("FeedPS failed - no target cursor", HUE_WARN)
                        API.CancelTarget()

                    API.Msg("[feedarti")
                    API.WaitForTarget()
                    if API.HasTarget():
                        API.Target(pet_serial)
                    else:
                        debug_msg("FeedArti failed - no target cursor", HUE_WARN)
                        API.CancelTarget()
                elif feed_mode != 3:
                    debug_msg("Feeding skipped - chosen pet missing or invalid", HUE_WARN)

            API.CreateCooldownBar(FEED_DELAY, "Feeding", HUE_INFO)
            last_feed_time = now
            continue

        if use_potions and now - last_potion_time >= POTION_DELAY:
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
    #API.Pause(CHECK_DELAY)


# ----------------------------------------------------------
# Shutdown
# ----------------------------------------------------------

API.OnHotKey("CTRL+SHIFT+P")
API.OnHotKey("CTRL+SHIFT+O")

close_config()

if status_gump and not status_gump.IsDisposed:
    status_gump.Dispose()

API.SysMsg("Aegis offline", HUE_PARAGON)