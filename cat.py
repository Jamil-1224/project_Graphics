"""
Village Scenario - simple 2D OpenGL project in Python (PyOpenGL + GLUT)

Features: house, sun/moon, moving clouds, trees, flying birds,
          moving ship on a river, smooth day/night cycle.

Controls:  D = day   N = night   Space = pause   ESC = quit

Install:   pip install PyOpenGL PyOpenGL_accelerate
Run:       python village.py

Note (Windows): if glutInit fails, install freeglut. Easiest way is
           pip install PyOpenGL-accelerate and download a freeglut.dll
           (from the PyOpenGL "Windows binaries" page) into the project folder.
"""
import math
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

W, H = 1000, 600

# ---------- animation state ----------
state = {
    "cloud_x": 0.0,
    "ship_x": 0.0,
    "bird_x": 0.0,
    "t": 0.0,
    "night_mix": 0.0,      # 0 = full day, 1 = full night
    "night_target": False,
    "paused": False,
}


# ---------- helpers ----------
def shade():
    return 1.0 - 0.65 * state["night_mix"]


def col(r, g, b):
    s = shade()
    glColor3f(r * s, g * s, b * s)


def rect(x1, y1, x2, y2):
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()


def tri(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()


def circle(cx, cy, r, segments=40):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + r * math.cos(a), cy + r * math.sin(a))
    glEnd()


def lerp(a, b, m):
    return a * (1 - m) + b * m


# ---------- scene objects ----------
def draw_sky():
    m = state["night_mix"]
    top_d, bot_d = (0.25, 0.55, 0.95), (0.70, 0.88, 1.00)
    top_n, bot_n = (0.02, 0.03, 0.12), (0.08, 0.10, 0.25)
    glBegin(GL_QUADS)
    glColor3f(*[lerp(bot_d[i], bot_n[i], m) for i in range(3)])
    glVertex2f(0, 200)
    glVertex2f(W, 200)
    glColor3f(*[lerp(top_d[i], top_n[i], m) for i in range(3)])
    glVertex2f(W, H)
    glVertex2f(0, H)
    glEnd()


def draw_stars():
    if state["night_mix"] < 0.3:
        return
    t = state["t"]
    glColor3f(1, 1, 1)
    glPointSize(2)
    glBegin(GL_POINTS)
    for i in range(60):
        x = (i * 173.0) % W
        y = 300 + (i * 97.0) % 290
        if math.sin(t * 3 + i) > -0.6:       # twinkle
            glVertex2f(x, y)
    glEnd()


def draw_sun_moon():
    t = state["t"]
    if state["night_mix"] < 0.5:
        glColor3f(1.0, 0.85, 0.1)
        circle(820, 500, 45)
        glColor3f(1.0, 0.9, 0.3)
        glLineWidth(2)
        glBegin(GL_LINES)
        for i in range(12):
            a = 2 * math.pi * i / 12 + t * 0.3
            glVertex2f(820 + 55 * math.cos(a), 500 + 55 * math.sin(a))
            glVertex2f(820 + 75 * math.cos(a), 500 + 75 * math.sin(a))
        glEnd()
    else:
        # crescent moon: pale disc + sky-coloured disc
        glColor3f(0.95, 0.95, 0.85)
        circle(820, 500, 40)
        glColor3f(0.03, 0.05, 0.16)
        circle(840, 510, 36)


def cloud(x, y, s):
    g = 1.0 - 0.55 * state["night_mix"]
    glColor3f(g, g, g)
    circle(x, y, 22 * s)
    circle(x + 25 * s, y + 8 * s, 28 * s)
    circle(x + 55 * s, y, 24 * s)
    circle(x + 28 * s, y - 8 * s, 24 * s)


def draw_clouds():
    cx = state["cloud_x"]
    cloud((cx + 100) % (W + 200) - 100, 520, 1.0)
    cloud((cx * 0.7 + 450) % (W + 200) - 100, 470, 1.3)
    cloud((cx * 1.2 + 750) % (W + 200) - 100, 550, 0.8)


def draw_hills():
    col(0.20, 0.50, 0.22)
    tri(-100, 230, 250, 340, 600, 230)
    col(0.15, 0.42, 0.18)
    tri(300, 230, 650, 380, 1050, 230)
    col(0.25, 0.55, 0.25)
    tri(650, 230, 900, 320, 1200, 230)


def draw_river():
    t = state["t"]
    col(0.15, 0.45, 0.80)
    rect(0, 150, W, 232)
    col(0.55, 0.78, 0.95)
    glLineWidth(2)
    glBegin(GL_LINES)
    for i in range(14):
        x = (i * 83.0 + t * 20) % W
        y = 165 + (i % 4) * 16
        glVertex2f(x, y)
        glVertex2f(x + 25, y)
    glEnd()


def draw_ship():
    t = state["t"]
    x = state["ship_x"] % (W + 300) - 200
    y = 175 + 3 * math.sin(t * 2)            # gentle bobbing

    # hull
    col(0.55, 0.15, 0.12)
    glBegin(GL_QUADS)
    glVertex2f(x, y + 30)
    glVertex2f(x + 150, y + 30)
    glVertex2f(x + 125, y)
    glVertex2f(x + 25, y)
    glEnd()
    # cabin
    col(0.92, 0.92, 0.92)
    rect(x + 40, y + 30, x + 110, y + 60)
    # funnel
    col(0.85, 0.2, 0.2)
    rect(x + 65, y + 60, x + 85, y + 82)
    col(0.1, 0.1, 0.1)
    rect(x + 65, y + 76, x + 85, y + 82)
    # portholes
    col(0.3, 0.6, 0.9)
    for px in (55, 75, 95):
        circle(x + px, y + 45, 5)
    # mast + flag
    col(0.2, 0.2, 0.2)
    rect(x + 118, y + 30, x + 121, y + 75)
    col(1.0, 0.8, 0.0)
    tri(x + 121, y + 75, x + 121, y + 62, x + 140, y + 68)
    # smoke puffs
    g = 0.7 - 0.3 * state["night_mix"]
    glColor3f(g, g, g)
    for i in range(3):
        k = (t * 0.8 + i * 0.33) % 1.0
        circle(x + 75 - 40 * k, y + 85 + 40 * k, 6 + 8 * k)


def draw_ground():
    col(0.30, 0.65, 0.25)
    rect(0, 0, W, 150)
    # road
    col(0.35, 0.35, 0.38)
    rect(0, 15, W, 55)
    col(0.95, 0.95, 0.95)
    for x in range(10, W, 80):
        rect(x, 33, x + 40, 37)


def draw_house(x, y):
    # walls
    col(0.95, 0.80, 0.55)
    rect(x, y, x + 220, y + 110)
    # roof
    col(0.70, 0.18, 0.15)
    tri(x - 20, y + 110, x + 240, y + 110, x + 110, y + 190)
    # chimney
    col(0.45, 0.25, 0.20)
    rect(x + 160, y + 140, x + 185, y + 185)
    # door
    col(0.40, 0.22, 0.10)
    rect(x + 90, y, x + 135, y + 70)
    col(1.0, 0.85, 0.2)
    circle(x + 126, y + 35, 3)
    # windows (glow at night)
    for wx in (x + 20, x + 160):
        if state["night_mix"] > 0.5:
            glColor3f(1.0, 0.9, 0.4)
        else:
            glColor3f(0.65, 0.85, 1.0)
        rect(wx, y + 50, wx + 40, y + 90)
        glColor3f(0.3, 0.2, 0.1)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(wx + 20, y + 50)
        glVertex2f(wx + 20, y + 90)
        glVertex2f(wx, y + 70)
        glVertex2f(wx + 40, y + 70)
        glEnd()


def draw_tree(x, y, s):
    col(0.45, 0.28, 0.12)
    rect(x - 8 * s, y, x + 8 * s, y + 60 * s)
    col(0.10, 0.50, 0.15)
    circle(x, y + 85 * s, 38 * s)
    circle(x - 28 * s, y + 65 * s, 28 * s)
    circle(x + 28 * s, y + 65 * s, 28 * s)
    col(0.15, 0.58, 0.20)
    circle(x, y + 105 * s, 26 * s)


def bird(x, y, s, phase):
    flap = math.sin(state["t"] * 8 + phase) * 8 * s
    glColor3f(0.1, 0.1, 0.1)
    glLineWidth(2)
    glBegin(GL_LINE_STRIP)
    glVertex2f(x - 14 * s, y + flap)
    glVertex2f(x, y)
    glVertex2f(x + 14 * s, y + flap)
    glEnd()


def draw_birds():
    if state["night_mix"] > 0.7:             # birds sleep at night
        return
    t = state["t"]
    x = state["bird_x"] % (W + 200) - 100
    bird(x,       430 + 10 * math.sin(t),     1.0, 0)
    bird(x - 50,  410 + 10 * math.sin(t + 1), 0.8, 1)
    bird(x - 90,  445 + 10 * math.sin(t + 2), 0.9, 2)
    bird(x - 130, 420 + 10 * math.sin(t + 3), 0.7, 3)


# ---------- GLUT callbacks ----------
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_sky()
    draw_stars()
    draw_sun_moon()
    draw_clouds()
    draw_hills()
    draw_river()
    draw_ship()
    draw_ground()
    draw_tree(620, 60, 1.0)
    draw_tree(730, 70, 1.3)
    draw_tree(900, 60, 1.1)
    draw_tree(60, 70, 1.2)
    draw_house(190, 60)
    draw_birds()
    glutSwapBuffers()


def update(_value):
    s = state
    if not s["paused"]:
        s["t"] += 0.016
        s["cloud_x"] += 0.6
        s["ship_x"] += 1.2
        s["bird_x"] += 2.0
        # smooth day/night transition
        target = 1.0 if s["night_target"] else 0.0
        if s["night_mix"] < target:
            s["night_mix"] = min(target, s["night_mix"] + 0.01)
        elif s["night_mix"] > target:
            s["night_mix"] = max(target, s["night_mix"] - 0.01)
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def keyboard(key, _x, _y):
    k = key.decode("utf-8", errors="ignore") if isinstance(key, bytes) else key
    if k in ("d", "D"):
        state["night_target"] = False
    elif k in ("n", "N"):
        state["night_target"] = True
    elif k == " ":
        state["paused"] = not state["paused"]
    elif k == "\x1b":                        # ESC
        sys.exit(0)


def init():
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(100, 60)
    glutCreateWindow(b"Village Scenario - OpenGL (Python)")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(16, update, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()