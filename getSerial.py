import API

item = API.RequestTarget(timeout=10)

if item:
    potion = API.FindItem(item)

    if potion:
        API.SysMsg("Graphic: " + hex(potion.Graphic))
        API.SysMsg("Hue: " + str(potion.Hue))
        API.SysMsg("Serial: " + hex(potion.Serial))