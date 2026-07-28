import API
import time

# ==========================================================
# Buffs - Standalone Buff Maintenance
# ==========================================================

# ----- Toggles (True = enabled) -----
USE_PRIMARY_ABILITY   = False   #Pick one of these it will overwrite the others
USE_SECONDARY_ABILITY = True    #Pick one of these it will overwrite the others
USE_MOMENTUM          = False   #Pick one of these it will overwrite the others
USE_CONSECRATE        = False
USE_BLESS             = True
USE_IMMOLATING        = False
USE_BLOOD_OATH        = True
USE_REMOVE_CURSE      = True

# ----- Timing / thresholds -----
BUFF_CHECK_DELAY  = 0.35
CONSECRATE_DELAY  = 7.0
BLESS_DELAY       = 60.0
IMMOLATING_DELAY  = 7.5
BO_DELAY          = 10.0
HEAL_PERCENT      = 65          # only cast certain buffs if HP% is at or above this

# ==========================================================

last_consecrate = 0
last_immolating = 0
last_bo = 0
last_bless = 0

def hp_percent():
    if API.Player.HitsMax <= 0:
        return 100
    return (API.Player.Hits * 100.0) / API.Player.HitsMax

API.SysMsg("Buffs Maintenance Started", 68)

while not API.StopRequested:
    API.ProcessCallbacks()
    now = time.time()

    # Primary Ability
    if USE_PRIMARY_ABILITY:
        if not API.PrimaryAbilityActive():
            API.ToggleAbility("primary")

    # Secondary Ability
    if USE_SECONDARY_ABILITY:
        if not API.SecondaryAbilityActive():
            API.ToggleAbility("secondary")

    # Momentum Strike
    if USE_MOMENTUM:
        API.CastSpell("Momentum Strike")

    # Consecrate Weapon
    if USE_CONSECRATE and now - last_consecrate >= CONSECRATE_DELAY:
        if hp_percent() >= HEAL_PERCENT:
            API.CastSpell("Consecrate Weapon")
            last_consecrate = now
            API.Pause(BUFF_CHECK_DELAY)
        # else: skip but do NOT reset timer

    # Bless
    if USE_BLESS and now - last_bless >= BLESS_DELAY:
        if hp_percent() >= HEAL_PERCENT:
            API.CastSpell("Bless")
            API.WaitForTarget()
            API.TargetSelf()
            last_bless = now
        # else: skip but do NOT reset timer

    # Immolating Weapon
    if USE_IMMOLATING and now - last_immolating >= IMMOLATING_DELAY:
        if hp_percent() >= HEAL_PERCENT:
            API.CastSpell("Immolating Weapon")
            last_immolating = now
        # else: skip but do NOT reset timer

    # Blood Oath
    if USE_BLOOD_OATH and now - last_bo >= BO_DELAY:
        if hp_percent() >= HEAL_PERCENT:
            API.CastSpell("Blood Oath")
            API.WaitForTarget()
            API.TargetSelf()
            last_bo = now
        # else: skip but do NOT reset timer

    # Remove Curse
    if USE_REMOVE_CURSE:
        if (
            API.BuffExists("Weaken")
            or API.BuffExists("Clumsy")
            or API.BuffExists("Feeblemind")
            or API.BuffExists("Curse")
        ):
            API.CastSpell("Remove Curse")
            API.WaitForTarget()
            API.TargetSelf()

    API.Pause(BUFF_CHECK_DELAY)

API.SysMsg("Buffs Maintenance Stopped")