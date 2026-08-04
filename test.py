import API

GUMP = 0xAEBAA44B

buttons = [
    100, 101, 102, 103, 104, 108, 109, 110, 105, 106, 111, 112, 113
]
       
def wait_for_gump():
    while not API.HasGump(GUMP):
        API.Pause(0.1)

for button in buttons:
    for _ in range(2):
        API.ReplyGump(button, GUMP)
        wait_for_gump()  