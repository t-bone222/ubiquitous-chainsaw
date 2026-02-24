diff --git a/main.py b/main.py
index 10222f5f1ebb374d3d0f7cdab4c72090a3cce048..63f8d7d90fd5880fa03f1022781ec183b66a670c 100644
--- a/main.py
+++ b/main.py
@@ -1,103 +1,222 @@
 import tkinter as tk
-import math
-
-WIDTH, HEIGHT = 640, 480
-FOV = math.pi / 3
-HALF_FOV = FOV / 2
-NUM_RAYS = WIDTH // 2
-DELTA_ANGLE = FOV / NUM_RAYS
-MAX_DEPTH = 30
-SCALE = WIDTH // NUM_RAYS
-
-MAP = [
-    '############',
-    '#          #',
-    '#  ##      #',
-    '#     ###  #',
-    '#   ##     #',
-    '#          #',
-    '#   ###    #',
-    '#          #',
-    '############'
+from tkinter import messagebox
+
+TILE_SIZE = 32
+WORLD_MAP = [
+    "####################",
+    "#.................##",
+    "#....S.............#",
+    "#..................#",
+    "#..........I.......#",
+    "#..................#",
+    "#..................#",
+    "####################",
 ]
-TILE = 1
-
-player_x = 3.0
-player_y = 3.0
-player_angle = 0.0
-
-root = tk.Tk()
-root.title('Arena Style Demo')
-canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
-canvas.pack()
-
-
-def cast_ray(angle):
-    x, y = player_x, player_y
-    sin_a = math.sin(angle)
-    cos_a = math.cos(angle)
-    for depth in range(1, MAX_DEPTH * 100):
-        x += cos_a * 0.01
-        y += sin_a * 0.01
-        i, j = int(x), int(y)
-        if MAP[j][i] == '#':
-            dist = math.hypot(x - player_x, y - player_y)
-            return dist
-    return MAX_DEPTH
-
-
-def render():
-    canvas.delete('all')
-    start_angle = player_angle - HALF_FOV
-    for ray in range(NUM_RAYS):
-        angle = start_angle + ray * DELTA_ANGLE
-        dist = cast_ray(angle)
-        depth_correction = dist * math.cos(player_angle - angle)
-        depth_correction = max(depth_correction, 0.0001)
-        proj_height = min(int(HEIGHT / depth_correction), HEIGHT)
-        shade = int(255 / (1 + depth_correction ** 2 * 0.1))
-        color = f'#{shade:02x}{shade:02x}{shade:02x}'
-        x = ray * SCALE
-        canvas.create_rectangle(x, (HEIGHT - proj_height) // 2,
-                               x + SCALE, (HEIGHT + proj_height) // 2,
-                               fill=color, outline=color)
-    root.after(16, render)
-
-
-pressed_keys = set()
-
-
-def key_press(event):
-    pressed_keys.add(event.keysym)
-
-
-def key_release(event):
-    pressed_keys.discard(event.keysym)
-
-
-def update():
-    global player_x, player_y, player_angle
-    step = 0.05
-    rot = 0.05
-    if 'Up' in pressed_keys:
-        nx = player_x + math.cos(player_angle) * step
-        ny = player_y + math.sin(player_angle) * step
-        if MAP[int(ny)][int(nx)] == ' ':
-            player_x, player_y = nx, ny
-    if 'Down' in pressed_keys:
-        nx = player_x - math.cos(player_angle) * step
-        ny = player_y - math.sin(player_angle) * step
-        if MAP[int(ny)][int(nx)] == ' ':
-            player_x, player_y = nx, ny
-    if 'Left' in pressed_keys:
-        player_angle -= rot
-    if 'Right' in pressed_keys:
-        player_angle += rot
-    root.after(16, update)
-
-
-root.bind('<KeyPress>', key_press)
-root.bind('<KeyRelease>', key_release)
-update()
-render()
-root.mainloop()
+
+INTERIORS = {
+    "S": {
+        "name": "Shop",
+        "map": [
+            "##########",
+            "#........#",
+            "#.TTTT...#",
+            "#....K...#",
+            "#........#",
+            "##########",
+        ],
+        "start": (2, 4),
+        "color": "#5c3a1e",
+        "npc": "K",
+        "greeting": "Merchant: Welcome! Browse my wares.",
+    },
+    "I": {
+        "name": "Inn",
+        "map": [
+            "##########",
+            "#........#",
+            "#..BBBB..#",
+            "#....N...#",
+            "#........#",
+            "##########",
+        ],
+        "start": (2, 4),
+        "color": "#3b2d56",
+        "npc": "N",
+        "greeting": "Innkeeper: Rooms are warm and affordable.",
+    },
+}
+
+COLORS = {
+    "#": "#3b3b3b",
+    ".": "#2e6b3d",
+    "S": "#8b5a2b",
+    "I": "#5b4ea1",
+    "T": "#9a7b4f",
+    "B": "#7a6b9e",
+    "K": "#f0c97d",
+    "N": "#d4a3ff",
+    "player": "#ff5555",
+}
+
+
+class ArenaPOC:
+    def __init__(self) -> None:
+        self.root = tk.Tk()
+        self.root.title("Arena-Style Town Demo")
+
+        width = len(WORLD_MAP[0]) * TILE_SIZE
+        height = len(WORLD_MAP) * TILE_SIZE
+
+        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="#111111")
+        self.canvas.pack()
+
+        self.status = tk.StringVar()
+        self.status.set("Arrows/WASD: Move | E: Enter building | Q: Exit building")
+        self.status_label = tk.Label(self.root, textvariable=self.status, anchor="w")
+        self.status_label.pack(fill="x")
+
+        self.world_pos = [2, 2]
+        self.interior_id = None
+        self.interior_pos = [0, 0]
+
+        self.root.bind("<KeyPress>", self.on_key)
+        self.draw()
+        self.status.set(self.nearby_npc_message())
+
+    def active_map(self):
+        if self.interior_id:
+            return INTERIORS[self.interior_id]["map"]
+        return WORLD_MAP
+
+    def player_pos(self):
+        if self.interior_id:
+            return self.interior_pos
+        return self.world_pos
+
+    def set_player_pos(self, x, y):
+        if self.interior_id:
+            self.interior_pos = [x, y]
+        else:
+            self.world_pos = [x, y]
+
+    def tile_at(self, x, y):
+        game_map = self.active_map()
+        if y < 0 or y >= len(game_map) or x < 0 or x >= len(game_map[0]):
+            return "#"
+        row = game_map[y]
+        if x >= len(row):
+            return "#"
+        return row[x]
+
+    def can_walk(self, tile):
+        return tile != "#"
+
+    def move_player(self, dx, dy):
+        x, y = self.player_pos()
+        nx, ny = x + dx, y + dy
+        tile = self.tile_at(nx, ny)
+        if self.can_walk(tile):
+            self.set_player_pos(nx, ny)
+
+    def try_enter_building(self):
+        if self.interior_id:
+            return
+        x, y = self.world_pos
+        tile = self.tile_at(x, y)
+        if tile in INTERIORS:
+            self.interior_id = tile
+            sx, sy = INTERIORS[tile]["start"]
+            self.interior_pos = [sx, sy]
+            self.status.set(f"You entered the {INTERIORS[tile]['name']}. Press Q to leave.")
+        else:
+            self.status.set("Stand on S (shop) or I (inn) then press E.")
+
+    def exit_building(self):
+        if not self.interior_id:
+            return
+        name = INTERIORS[self.interior_id]["name"]
+        self.interior_id = None
+        self.status.set(f"You left the {name}.")
+
+    def nearby_npc_message(self):
+        if not self.interior_id:
+            return "Explore town. Visit S=Shop, I=Inn."
+        npc = INTERIORS[self.interior_id]["npc"]
+        greeting = INTERIORS[self.interior_id]["greeting"]
+        x, y = self.interior_pos
+        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
+            if self.tile_at(x + ox, y + oy) == npc:
+                return greeting
+        return f"Inside {INTERIORS[self.interior_id]['name']}. Find the keeper to chat."
+
+    def on_key(self, event):
+        key = event.keysym.lower()
+        if key in {"up", "w"}:
+            self.move_player(0, -1)
+        elif key in {"down", "s"}:
+            self.move_player(0, 1)
+        elif key in {"left", "a"}:
+            self.move_player(-1, 0)
+        elif key in {"right", "d"}:
+            self.move_player(1, 0)
+        elif key == "e":
+            self.try_enter_building()
+        elif key == "q":
+            self.exit_building()
+
+        self.status.set(self.nearby_npc_message())
+        self.draw()
+
+    def draw_tile(self, x, y, tile):
+        px = x * TILE_SIZE
+        py = y * TILE_SIZE
+
+        if self.interior_id:
+            floor = INTERIORS[self.interior_id]["color"] if tile == "." else COLORS.get(tile, "#888")
+        else:
+            floor = COLORS.get(tile, "#888")
+
+        self.canvas.create_rectangle(
+            px,
+            py,
+            px + TILE_SIZE,
+            py + TILE_SIZE,
+            fill=floor,
+            outline="#222222",
+        )
+
+        if tile in {"S", "I"}:
+            label = "SHOP" if tile == "S" else "INN"
+            self.canvas.create_text(px + TILE_SIZE // 2, py + TILE_SIZE // 2, text=label, fill="white", font=("Arial", 8, "bold"))
+        elif tile in {"K", "N"}:
+            label = "MERCH" if tile == "K" else "INNKEEP"
+            self.canvas.create_text(px + TILE_SIZE // 2, py + TILE_SIZE // 2, text=label, fill="black", font=("Arial", 7, "bold"))
+
+    def draw(self):
+        game_map = self.active_map()
+        self.canvas.delete("all")
+
+        map_w = len(game_map[0]) * TILE_SIZE
+        map_h = len(game_map) * TILE_SIZE
+        self.canvas.config(width=map_w, height=map_h)
+
+        for y, row in enumerate(game_map):
+            for x, tile in enumerate(row):
+                self.draw_tile(x, y, tile)
+
+        x, y = self.player_pos()
+        px = x * TILE_SIZE + TILE_SIZE // 2
+        py = y * TILE_SIZE + TILE_SIZE // 2
+        radius = TILE_SIZE // 3
+        self.canvas.create_oval(px - radius, py - radius, px + radius, py + radius, fill=COLORS["player"], outline="white", width=2)
+
+
+if __name__ == "__main__":
+    try:
+        app = ArenaPOC()
+        app.root.mainloop()
+    except Exception as exc:
+        root = tk.Tk()
+        root.withdraw()
+        messagebox.showerror("Arena demo error", f"The game could not start:\n\n{exc}")
+        raise
