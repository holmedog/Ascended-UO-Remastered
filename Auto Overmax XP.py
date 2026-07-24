import API
import time

# ==========================================================
# Auto Reply + Close Gump Every 15 Seconds
# ==========================================================

GUMP_ID = 8002
BUTTON_ID = 0x86015E3F

API.SysMsg("Auto Gump Reply + Close started (every 15s)", 68)

while not API.StopRequested:
    # Reply to the button
    API.ReplyGump(GUMP_ID, BUTTON_ID)    
    API.Pause(15.0)