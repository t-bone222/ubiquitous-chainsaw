import tkinter as tk
import math

WIDTH, HEIGHT = 640, 480
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
SCALE = WIDTH // NUM_RAYS

MAP = [
    '########',
    '#      #',
    '#      #',
    '#  ##  #',
    '#      #',
    '########'
]
TILE = 1

player_x = 3.0
player_y = 3.0
player_angle = 0.0

root = tk.Tk()
root.title('Arena Style Demo')
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()


def cast_ray(angle):
    x, y = player_x, player_y
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    for depth in range(1, MAX_DEPTH * 100):
        x += cos_a * 0.01
        y += sin_a * 0.01
        i, j = int(x), int(y)
        if MAP[j][i] == '#':
            dist = math.hypot(x - player_x, y - player_y)
            return dist
    return MAX_DEPTH


def render():
    canvas.delete('all')
    start_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * DELTA_ANGLE
        dist = cast_ray(angle)
        depth_correction = dist * math.cos(player_angle - angle)
        depth_correction = max(depth_correction, 0.0001)
        proj_height = min(int(HEIGHT / depth_correction), HEIGHT)
        shade = int(255 / (1 + depth_correction ** 2 * 0.1))
        color = f'#{shade:02x}{shade:02x}{shade:02x}'
        x = ray * SCALE
        canvas.create_rectangle(x, (HEIGHT - proj_height) // 2,
                               x + SCALE, (HEIGHT + proj_height) // 2,
                               fill=color, outline=color)
    root.after(30, render)


def move(event):
    global player_x, player_y, player_angle
    step = 0.1
    if event.keysym == 'Up':
        nx = player_x + math.cos(player_angle) * step
        ny = player_y + math.sin(player_angle) * step
        if MAP[int(ny)][int(nx)] == ' ':
            player_x, player_y = nx, ny
    elif event.keysym == 'Down':
        nx = player_x - math.cos(player_angle) * step
        ny = player_y - math.sin(player_angle) * step
        if MAP[int(ny)][int(nx)] == ' ':
            player_x, player_y = nx, ny
    elif event.keysym == 'Left':
        player_angle -= 0.1
    elif event.keysym == 'Right':
        player_angle += 0.1


root.bind('<KeyPress>', move)
render()
root.mainloop()
