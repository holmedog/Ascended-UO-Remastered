import API
import time

# ==========================================================
# Smart Keep Alive – Options
# ==========================================================

# ----- Toggles (True = enabled) -----
HEAL_SELF        = False
CURE_SELF        = False
HEAL_PETS        = False
CURE_PETS        = False
RESURRECT_PETS   = True
REMOVE_CURSE     = False

# ----- Settings -----
HEAL_PERCENT     = 92          # heal when HP% is at or below this
CHECK_DELAY      = 0.25
CURE_SPELL       = "Cleanse by Fire"
HEAL_SPELL       = "Greater Heal"
RES_GUMP_ID      = 0x04DA72C0  # resurrection confirmation gump

# ==========================================================

pet1_serial = 0
pet2_serial = 0

def hp_percent():
    if API.Player.HitsMax <= 0:
        return 100
    return (API.Player.Hits * 100.0) / API.Player.HitsMax

def mobile_hp_percent(mobile):
    if not mobile or not hasattr(mobile, 'HitsMax') or mobile.HitsMax <= 0:
        return 100
    return (mobile.Hits * 100.0) / mobile.HitsMax

def resurrect_pet(pet_serial):
    """Cast Resurrection on a dead pet and confirm the gump."""
    API.CastSpell("Resurrection")
    if not API.WaitForTarget(timeout=3):
        return False
    API.Target(pet_serial)

    # Wait for the confirmation gump
    timeout = time.time() + 5
    while not API.HasGump(RES_GUMP_ID) and time.time() < timeout:
        API.Pause(0.1)

    if API.HasGump(RES_GUMP_ID):
        API.ReplyGump(1, RES_GUMP_ID)
        API.SysMsg("Resurrected pet", 68)
        return True
    return False

API.SysMsg("Smart Keep Alive Started", 68)

# Select companions
API.Msg("Target companion #1")
pet1_serial = API.RequestTarget(timeout=8)
API.Msg("Target companion #2")
pet2_serial = API.RequestTarget(timeout=8)

while not API.StopRequested:
    API.ProcessCallbacks()

    if API.Player.IsDead:
        API.Pause(CHECK_DELAY)
        continue

    # ----- Cure Poison (Self) -----
    if CURE_SELF and API.Player.IsPoisoned:
        API.CastSpell(CURE_SPELL)
        API.WaitForTarget()
        API.TargetSelf()
        continue

    # ----- Heal Self -----
    if HEAL_SELF and hp_percent() <= HEAL_PERCENT:
        API.CastSpell(HEAL_SPELL)
        API.WaitForTarget()
        API.TargetSelf()
        continue

    # ----- Pet care -----
    for pet_serial in [pet1_serial, pet2_serial]:
        if not pet_serial:
            continue

        pet = API.FindMobile(pet_serial)
        if not pet:
            continue

        # Resurrect dead pet
        if RESURRECT_PETS and pet.IsDead:
            resurrect_pet(pet_serial)
            continue

        # Skip further pet actions if dead (and we didn't just res)
        if pet.IsDead:
            continue

        # Cure pet
        if CURE_PETS and pet.IsPoisoned:
            API.CastSpell(CURE_SPELL)
            API.WaitForTarget()
            API.Target(pet_serial)
            continue

        # Heal pet
        if HEAL_PETS and mobile_hp_percent(pet) <= HEAL_PERCENT:
            API.CastSpell(HEAL_SPELL)
            API.WaitForTarget()
            API.Target(pet_serial)
            continue

    # ----- Remove Curse (Self) -----
    if REMOVE_CURSE and (
        API.BuffExists("Weaken")
        or API.BuffExists("Clumsy")
        or API.BuffExists("Feeblemind")
        or API.BuffExists("Curse")
    ):
        API.CastSpell("Remove Curse")
        API.WaitForTarget()
        API.TargetSelf()

    API.Pause(CHECK_DELAY)

API.SysMsg("Smart Keep Alive Stopped")