import API

THRESHOLD = 15  # tiles (Manhattan)

# Starting position
last_x = API.Player.X
last_y = API.Player.Y
last_z = API.Player.Z

# Store points as (x, y, z)
points = [(last_x, last_y, last_z)]

API.SysMsg(f"Waypoint recorder started. Threshold = {THRESHOLD}", 68)
API.SysMsg(f"Start: ({last_x}, {last_y}, {last_z})", 68)

try:
    while not API.StopRequested:
        current_x = API.Player.X
        current_y = API.Player.Y
        current_z = API.Player.Z

        dist = abs(current_x - last_x) + abs(current_y - last_y)

        if dist > THRESHOLD:
            points.append((current_x, current_y, current_z))

            API.SysMsg(
                f"New waypoint ({len(points)}): ({current_x}, {current_y}, {current_z})  "
                f"[{dist} tiles]",
                53
            )

            last_x = current_x
            last_y = current_y
            last_z = current_z

        API.Pause(0.25)

finally:
    # This runs when you stop the script
    output_path = API.ScriptPath + "/waypoints.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        for x, y, z in points:
            f.write(f"    ({x}, {y}, {z}),\n")

    API.SysMsg(f"Saved {len(points)} waypoints → {output_path}", 68)