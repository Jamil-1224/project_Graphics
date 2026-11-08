"""
3D SUNDARBANS ENVIRONMENTAL SIMULATION
Python + Pygame + PyOpenGL (NO BLENDER)

Controls:
  W / S       Move camera forward / backward
  A / D       Move camera left / right
  Q / E       Move camera up / down
  LEFT/RIGHT  Rotate camera
  SPACE       Pause / resume boat
  ESC         Exit

Run:
  python sundarbans_opengl.py
"""

import math
import random
import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE
from OpenGL.GL import *
from OpenGL.GLU import *

# -------------------- WINDOW / OPENGL --------------------
WIDTH, HEIGHT = 1200, 760
pygame.init()
pygame.display.set_caption("Sundarbans 3D Simulation | Refined OpenGL Scene")
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
clock = pygame.time.Clock()

glViewport(0, 0, WIDTH, HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(55, WIDTH / HEIGHT, 0.1, 180.0)
glMatrixMode(GL_MODELVIEW)

# Enable depth, materials, smooth shading and lighting
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)
glShadeModel(GL_SMOOTH)
glEnable(GL_NORMALIZE)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_LIGHT1)

# Directional sunlight
glLightfv(GL_LIGHT0, GL_POSITION, (-0.45, 0.85, 0.35, 0.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 0.88, 0.68, 1.0))
glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 0.92, 0.78, 1.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.22, 0.24, 0.27, 1.0))

# Soft blue fill light
glLightfv(GL_LIGHT1, GL_POSITION, (0.0, 5.0, 3.0, 1.0))
glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.25, 0.48, 0.62, 1.0))
glLightfv(GL_LIGHT1, GL_AMBIENT, (0.04, 0.07, 0.09, 1.0))

# Atmospheric fog
glEnable(GL_FOG)
glFogi(GL_FOG_MODE, GL_EXP2)
glFogfv(GL_FOG_COLOR, (0.48, 0.62, 0.62, 1.0))
glFogf(GL_FOG_DENSITY, 0.008)
glHint(GL_FOG_HINT, GL_NICEST)

# Material defaults
glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.25, 0.25, 0.25, 1.0))
glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 28.0)

quadric = gluNewQuadric()
gluQuadricNormals(quadric, GLU_SMOOTH)

# -------------------- BASIC 3D HELPERS --------------------
def set_material(color, specular=(0.15, 0.15, 0.15, 1), shininess=18):
    glColor4f(*color, 1.0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

def cube(x, y, z, sx, sy, sz, color):
    """Draw a lit cube centred at x,y,z."""
    set_material(color)
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    faces = [
        ((0, 0, 1), [(-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]),
        ((0, 0,-1), [(hx,-hy,-hz),(-hx,-hy,-hz),(-hx,hy,-hz),(hx,hy,-hz)]),
        ((1, 0, 0), [(hx,-hy,hz),(hx,-hy,-hz),(hx,hy,-hz),(hx,hy,hz)]),
        ((-1,0, 0),[(-hx,-hy,-hz),(-hx,-hy,hz),(-hx,hy,hz),(-hx,hy,-hz)]),
        ((0, 1, 0), [(-hx,hy,hz),(hx,hy,hz),(hx,hy,-hz),(-hx,hy,-hz)]),
        ((0,-1, 0), [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,-hy,hz),(-hx,-hy,hz)])
    ]
    glPushMatrix()
    glTranslatef(x, y, z)
    glBegin(GL_QUADS)
    for normal, vertices in faces:
        glNormal3f(*normal)
        for v in vertices:
            glVertex3f(*v)
    glEnd()
    glPopMatrix()

def sphere(x, y, z, radius, color, scale=(1,1,1)):
    set_material(color, shininess=12)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(*scale)
    gluSphere(quadric, radius, 16, 12)
    glPopMatrix()

def cylinder_between(a, b, radius, color, slices=10):
    """Cylinder from point a to point b."""
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx-ax, by-ay, bz-az
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length < 0.0001:
        return
    set_material(color, shininess=8)
    glPushMatrix()
    glTranslatef(ax, ay, az)
    direction = (dx, dy, dz)
    z_axis = (0, 1, 0)
    dot = max(-1.0, min(1.0, dy / length))
    angle = math.degrees(math.acos(dot))
    axis = (dz, 0, -dx)
    if abs(angle) > 0.001 and (abs(axis[0]) + abs(axis[2])) > 0.001:
        glRotatef(angle, axis[0], axis[1], axis[2])
    gluCylinder(quadric, radius, radius*0.55, length, slices, 1)
    glPopMatrix()

# -------------------- ENVIRONMENT --------------------
def draw_ground():
    # Soil base
    set_material((0.20, 0.12, 0.065), shininess=3)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-32, -1.15, -24)
    glVertex3f(32, -1.15, -24)
    glVertex3f(32, -1.15, 24)
    glVertex3f(-32, -1.15, 24)
    glEnd()

    # Natural muddy banks beside the river.
    set_material((0.25, 0.18, 0.095), shininess=4)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    for z1, z2 in [(-6.0, -4.25), (4.25, 6.0)]:
        glVertex3f(-32, -1.105, z1)
        glVertex3f(32, -1.105, z1)
        glVertex3f(32, -1.105, z2)
        glVertex3f(-32, -1.105, z2)
    glEnd()

def draw_river():
    # River surface with reflective-looking specular material
    set_material((0.025, 0.22, 0.25), specular=(0.65,0.78,0.82,1), shininess=90)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-32, -0.98, -4.3)
    glVertex3f(32, -0.98, -4.3)
    glVertex3f(32, -0.98, 4.3)
    glVertex3f(-32, -0.98, 4.3)
    glEnd()

    # Fine water ripple lines
    glDisable(GL_LIGHTING)
    for i in range(34):
        x = -30 + i * 1.8
        z = math.sin(i * 1.7) * 3.3
        glColor3f(0.12, 0.42, 0.46)
        glBegin(GL_LINES)
        glVertex3f(x, -0.955, z)
        glVertex3f(x + 0.9, -0.955, z + 0.12)
        glEnd()
    glEnable(GL_LIGHTING)

def draw_tree(x, z, scale=1.0):
    # Main trunk
    cylinder_between((x, -1.12, z), (x, 1.65*scale, z), 0.24*scale, (0.25,0.12,0.055), 12)

    # Mangrove prop roots
    for angle in (0, math.pi/2, math.pi, 3*math.pi/2):
        dx = math.cos(angle) * 0.85 * scale
        dz = math.sin(angle) * 0.85 * scale
        cylinder_between((x, -0.95, z), (x+dx, -1.12, z+dz),
                         0.105*scale, (0.31,0.16,0.075), 8)

    # Compact, layered leaf canopy: smaller clusters reduce visual overlap.
    canopy_offsets = [
        (-0.42, 1.82, -0.18), (0.38, 1.88, 0.16),
        (-0.12, 2.18, 0.38), (0.18, 2.20, -0.38),
        (0.02, 2.48, 0.02)
    ]
    for j, (ox, oy, oz) in enumerate(canopy_offsets):
        col = (0.045, 0.23, 0.075) if j % 2 else (0.075, 0.31, 0.10)
        sphere(x + ox*scale, oy*scale, z + oz*scale,
               0.48*scale, col, (1.18, 0.78, 1.0))

def draw_forest():
    # Staggered shoreline placement with generous gaps between tree canopies.
    random.seed(19)
    for side in (-1, 1):
        for i in range(9):
            x = -24 + i * 6.0 + random.uniform(-0.35, 0.35)
            z = side * (8.2 + (i % 2) * 1.35 + random.uniform(-0.25, 0.25))
            scale = random.uniform(0.78, 0.98)
            draw_tree(x, z, scale)

def draw_boat(x, bob):
    glPushMatrix()
    glTranslatef(x, -0.55 + bob, 0.0)

    # Hull
    set_material((0.42,0.12,0.045), specular=(0.35,0.22,0.12,1), shininess=35)
    glBegin(GL_QUADS)
    # top
    glNormal3f(0,1,0)
    glVertex3f(-2.0,0.45,-0.55); glVertex3f(2.0,0.45,-0.55)
    glVertex3f(2.0,0.45,0.55); glVertex3f(-2.0,0.45,0.55)
    # front and back hull faces
    glNormal3f(0,0,1)
    glVertex3f(-2.0,0.45,0.55); glVertex3f(2.0,0.45,0.55)
    glVertex3f(1.45,-0.12,0.42); glVertex3f(-1.45,-0.12,0.42)
    glNormal3f(0,0,-1)
    glVertex3f(2.0,0.45,-0.55); glVertex3f(-2.0,0.45,-0.55)
    glVertex3f(-1.45,-0.12,-0.42); glVertex3f(1.45,-0.12,-0.42)
    glEnd()

    # Cabin and blue glass
    cube(-0.25, 0.88, 0, 1.25, 0.82, 0.88, (0.55,0.29,0.10))
    cube(0.40, 0.91, 0.01, 0.035, 0.48, 0.57, (0.08,0.42,0.53))
    cube(-0.25, 0.91, 0.45, 0.66, 0.48, 0.035, (0.08,0.42,0.53))

    # Roof
    cube(-0.25, 1.34, 0, 1.48, 0.12, 1.05, (0.16,0.075,0.035))
    # Bow trim
    cylinder_between((1.5,0.1,0),(2.05,0.38,0),0.045,(0.9,0.58,0.16),8)

    glPopMatrix()

def draw_sun_glow():
    # Stylized sun disc; lighting is also provided by GL_LIGHT0
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.78, 0.42)
    glPushMatrix()
    glTranslatef(-10, 10, -15)
    gluSphere(quadric, 1.25, 20, 16)
    glPopMatrix()
    glEnable(GL_LIGHTING)

# -------------------- MAIN LOOP --------------------
camera_x, camera_y, camera_z = 0.0, 5.2, 27.0
yaw = 0.0
boat_x = -20.0
boat_paused = False
elapsed = 0.0
running = True

while running:
    dt = min(clock.tick(60) / 1000.0, 0.04)
    elapsed += dt

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                boat_paused = not boat_paused

    keys = pygame.key.get_pressed()
    move_speed = 9.0 * dt
    if keys[pygame.K_w]:
        camera_z -= move_speed
    if keys[pygame.K_s]:
        camera_z += move_speed
    if keys[pygame.K_a]:
        camera_x -= move_speed
    if keys[pygame.K_d]:
        camera_x += move_speed
    if keys[pygame.K_q]:
        camera_y += move_speed
    if keys[pygame.K_e]:
        camera_y -= move_speed
    if keys[pygame.K_LEFT]:
        yaw += 55 * dt
    if keys[pygame.K_RIGHT]:
        yaw -= 55 * dt

    if not boat_paused:
        boat_x += 4.0 * dt
        if boat_x > 22:
            boat_x = -22

    # Clear with fog-matching background
    glClearColor(0.48, 0.62, 0.62, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    look_x = camera_x + math.sin(math.radians(yaw)) * 12
    look_z = camera_z - math.cos(math.radians(yaw)) * 12
    gluLookAt(camera_x, camera_y, camera_z,
              look_x, 1.0, look_z,
              0, 1, 0)

    # Reposition camera-dependent point light
    glLightfv(GL_LIGHT1, GL_POSITION, (camera_x, camera_y+2, camera_z-2, 1.0))

    draw_sun_glow()
    draw_ground()
    draw_river()
    draw_forest()

    bob = math.sin(elapsed * 2.3) * 0.07
    draw_boat(boat_x, bob)

    pygame.display.flip()

pygame.quit()
sys.exit()
