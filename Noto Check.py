import API

API.RequestTarget()

API.WaitForTarget()

target = API.LastTargetSerial

if target:
    mob = API.FindMobile(target)

    if mob:
        API.SysMsg("Name: " + str(mob.Name))
        API.SysMsg("Serial: " + str(mob.Serial))
        API.SysMsg("Notoriety: " + str(mob.Notoriety))
    else:
        API.SysMsg("Target is not a mobile")
else:
    API.SysMsg("No target selected")