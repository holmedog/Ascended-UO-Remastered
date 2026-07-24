import API
import time

# ==========================================================
# Persistent Potion Timer
# ==========================================================

POTION_DELAY = 590      # ~9min 50s
POTION_GAP = 5
HUE_INFO = 88

VAR_LAST_POTION = "potion_last_use_time"

# Load saved time on start
last_use_time = float(API.GetPersistentVar(VAR_LAST_POTION, "0", API.PersistentVar.Char))

API.SysMsg("Potion Timer Started - Last use: " + str(int(last_use_time)), HUE_INFO)

while not API.StopRequested:
    API.ProcessCallbacks()
    current_time = time.time()

    if current_time - last_use_time >= POTION_DELAY:
        API.SysMsg("Using Star Potion", HUE_INFO)
        API.UseType(0x0F09, 2902)
        
        API.Pause(POTION_GAP)

        API.SysMsg("Using Potion of Greed", HUE_INFO)
        API.UseType(0x0F09, 2910)

        last_use_time = current_time
        
        # Save to persistent storage
        API.SavePersistentVar(VAR_LAST_POTION, str(last_use_time), API.PersistentVar.Char)
        
        API.CreateCooldownBar(POTION_DELAY, "Potions", HUE_INFO)

    API.Pause(1.0)

API.SysMsg("Potion Timer Stopped")