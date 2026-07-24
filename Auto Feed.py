import API
import time

# ==========================================================
# Companion Feeder
# Prompts for pets on start. If none are set, just fires the macros.
# Feeds every 15 seconds.
# ==========================================================

FEED_DELAY = 15          # seconds between feed cycles
PAUSE_BETWEEN = 0.4

pet1_serial = 0
pet2_serial = 0
last_feed_time = 0


def get_pet_serial(slot):
    API.SysMsg(f"Target companion #{slot} (or cancel to skip)", 88)
    serial = API.RequestTarget(timeout=10)
    if serial:
        m = API.FindMobile(serial)
        name = m.Name if m and m.Name else f"0x{serial:X}"
        API.SysMsg(f"Companion #{slot} set: {name}", 68)
        return serial
    else:
        API.SysMsg(f"Companion #{slot} skipped", 53)
        return 0


# ----- Startup -----
API.SysMsg("Companion Feeder starting...", 88)

pet1_serial = get_pet_serial(1)
pet2_serial = get_pet_serial(2)

if not pet1_serial and not pet2_serial:
    API.SysMsg("No pets set - will fire macros without targeting", 53)
else:
    API.SysMsg("Pets configured - will target them when feeding", 68)

API.SysMsg("Companion Feeder online - feeding every 15s", 68)


# ----- Main Loop -----
while not API.StopRequested:

    now = time.time()

    if now - last_feed_time >= FEED_DELAY:

        pets = [s for s in (pet1_serial, pet2_serial) if s]

        if pets:
            # Target each configured pet
            for serial in pets:
                API.Msg("[feedps")
                API.Pause(PAUSE_BETWEEN)
                API.Target(serial)

                API.Msg("[feedarti")
                API.Pause(PAUSE_BETWEEN)
                API.Target(serial)
        else:
            # No pets set - just fire the macros
            API.Msg("[feedps")
            API.Pause(PAUSE_BETWEEN)
            API.Msg("[feedarti")
            API.Pause(PAUSE_BETWEEN)

        last_feed_time = now
        API.SysMsg("Fed companions", 68)

    API.Pause(0.5)