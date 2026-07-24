import API
import time

HEAL_PERCENT = 92
CHECK_DELAY = 0.25

CURE_SPELL = "Cleanse by Fire"
HEAL_SPELL = "Greater Heal"

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


API.SysMsg("Smart Keep Alive Started")

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

    # Cure Poison (Self)
    if API.Player.IsPoisoned:
        API.CastSpell(CURE_SPELL)
        API.WaitForTarget()
        API.TargetSelf()
        continue

    # Heal Self
    if hp_percent() <= HEAL_PERCENT:
        API.CastSpell(HEAL_SPELL)
        API.WaitForTarget()
        API.TargetSelf()
        continue

    # Pet Heals
    for pet_serial in [pet1_serial, pet2_serial]:
        if not pet_serial:
            continue
        pet = API.FindMobile(pet_serial)
        if not pet or pet.IsDead:
            continue

        if pet.IsPoisoned:
            API.CastSpell(CURE_SPELL)
            API.WaitForTarget()
            API.Target(pet_serial)
            continue

        if mobile_hp_percent(pet) <= HEAL_PERCENT:
            API.CastSpell(HEAL_SPELL)
            API.WaitForTarget()
            API.Target(pet_serial)
            continue

    # Remove Curse
    if (
        API.BuffExists("Weaken")
        or API.BuffExists("Clumsy")
        or API.BuffExists("Feeblemind")
        or API.BuffExists("Curse")
    ):        
        API.CastSpell("Remove Curse")
        API.WaitForTarget()
        API.TargetSelf()


API.SysMsg("Smart Keep Alive Stopped")