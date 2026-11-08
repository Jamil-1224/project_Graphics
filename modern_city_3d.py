import math
import random
import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *


pygame.init()
WIDTH, HEIGHT = 1280, 800
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Modern City 3D | Computer Graphics")

clock = pygame.time.Clock()
glu = GLUquadric = gluNewQuadric()
gluQuadricNormals(glu, GLU_SMOOTH)

# ---------- Scene / camera ----------
target = [0.0, 1.0, 0.0]
yaw = 42.0
pitch = 24.0
distance = 34.0
day_mode = True
fog_enabled = True
running = True
car_positions = [-18.0, 2.0, 17.0]
car_speeds = [5.0, 4.0, 6.0]
wheel_angle = 0.0

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def set_material(color, shine=24):
    glColor3f(*color)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (*color, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.28, 0.28, 0.28, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shine)

def cube(x, y, z, sx, sy, sz, color, shine=24):
    set_material(color, shine)
    x0, x1 = x-sx/2, x+sx/2
    y0, y1 = y-sy/2, y+sy/2
    z0, z1 = z-sz/2, z+sz/2
    glBegin(GL_QUADS)
    # Front (+z)
    glNormal3f(0,0,1)
    glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
    # Back (-z)
    glNormal3f(0,0,-1)
    glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0)
    # Right (+x)
    glNormal3f(1,0,0)
    glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1)
    # Left (-x)
    glNormal3f(-1,0,0)
    glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z1); glVertex3f(x0,y1,z1); glVertex3f(x0,y1,z0)
    # Top (+y)
    glNormal3f(0,1,0)
    glVertex3f(x0,y1,z1); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z0); glVertex3f(x0,y1,z0)
    # Bottom (-y)
    glNormal3f(0,-1,0)
    glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x1,y0,z0); glVertex3f(x1,y0,z1)
    glEnd()

def sphere(x, y, z, radius, color, scale=(1,1,1), shine=28):
    glPushMatrix()
    glTranslatef(x,y,z)
    glScalef(*scale)
    set_material(color, shine)
    gluSphere(glu, radius, 18, 14)
    glPopMatrix()

def cylinder_between(a, b, radius, color, slices=12):
    ax,ay,az = a
    bx,by,bz = b
    dx,dy,dz = bx-ax, by-ay, bz-az
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    if length < 0.0001:
        return
    glPushMatrix()
    glTranslatef(ax,ay,az)
    # Rotate cylinder's +Z axis to the segment direction.
    vx,vy,vz = dx/length,dy/length,dz/length
    dot = clamp(vz, -1.0, 1.0)
    angle = math.degrees(math.acos(dot))
    rx,ry,rz = -vy, vx, 0
    if abs(angle) > 0.001:
        glRotatef(angle, rx,ry,rz)
    set_material(color, 12)
    gluCylinder(glu, radius, radius, length, slices, 1)
    glPopMatrix()

def disk(x, y, z, radius, color, segments=32):
    set_material(color, 5)
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0,1,0)
    glVertex3f(x,y,z)
    for i in range(segments+1):
        a = 2*math.pi*i/segments
        glVertex3f(x+math.cos(a)*radius, y, z+math.sin(a)*radius)
    glEnd()

def draw_ground():
    cube(0, -0.22, 0, 62, 0.4, 48, (0.22,0.38,0.22))
    # Main road running along X
    cube(0, 0.015, 0, 62, 0.08, 9.0, (0.16,0.17,0.18), 8)
    # Sidewalks
    for z in (-5.3, 5.3):
        cube(0, 0.07, z, 62, 0.18, 1.5, (0.56,0.55,0.49), 8)
    # Lane markings
    for x in range(-29, 31, 5):
        cube(x, 0.07, 0, 2.6, 0.025, 0.13, (0.94,0.88,0.62), 3)
    # Road edge lines
    for z in (-4.25,4.25):
        cube(0,0.075,z,62,0.025,0.10,(0.88,0.87,0.78),3)
    # Crosswalk at central junction
    for i in range(7):
        cube(-1.5+i*0.5,0.085,3.15,0.28,0.025,1.35,(0.92,0.92,0.87),3)
    # Park lawn and paths
    cube(-15,0.02,13,17,0.08,13,(0.18,0.43,0.20))
    cube(-15,0.08,13,1.25,0.03,13,(0.68,0.64,0.53))
    cube(-15,0.09,13,17,0.03,1.15,(0.68,0.64,0.53))
    # Fountain basin
    cylinder_between((-15,0.12,13),(-15,0.12,13),0.1,(0.2,0.2,0.2))
    disk(-15,0.14,13,2.15,(0.35,0.39,0.40))
    disk(-15,0.19,13,1.72,(0.12,0.42,0.62))
    cylinder_between((-15,0.22,13),(-15,2.2,13),0.12,(0.72,0.75,0.78))
    sphere(-15,2.2,13,0.22,(0.28,0.68,0.88))

def draw_building(x, z, w, d, h, color, seed):
    # Distinct footprints, facades, roof cap, window grids and entrance.
    cube(x, h/2, z, w, h, d, color, 18)
    cube(x, h+0.12, z, w+0.25, 0.24, d+0.25, (0.23,0.27,0.31), 12)
    rng = random.Random(seed)
    cols = max(2, int(w/1.35))
    rows = max(2, int(h/1.65))
    for side in (-1,1):
        front_z = z + side*(d/2+0.012)
        for row in range(rows):
            for col in range(cols):
                wx = x-w/2+0.48+col*((w-0.75)/cols)
                wy = 1.0+row*((h-1.2)/rows)
                ww = min(0.58, (w-1.0)/cols*0.58)
                wh = min(0.78, (h-1.5)/rows*0.60)
                lit = rng.random() > 0.28
                window_color = (0.95,0.72,0.34) if (not day_mode and lit) else (0.23,0.48,0.60)
                cube(wx,wy,front_z,ww,wh,0.035,window_color,40)
    # Vertical facade strips for depth
    for side in (-1,1):
        cube(x+side*(w/2-0.08),h/2,z,0.12,h+0.02,d+0.04,(0.72,0.75,0.77),12)
    # Entrance
    cube(x,0.9,z+d/2+0.035,1.05,1.8,0.08,(0.12,0.18,0.22),12)
    cube(x,1.9,z+d/2+0.09,1.08,0.12,0.04,(0.80,0.82,0.83),20)
    # Rooftop utility boxes
    cube(x-w*0.23,h+0.55,z,1.2,0.65,1.1,(0.40,0.44,0.46),10)

def draw_tree(x,z,scale=1.0):
    cylinder_between((x,0.15,z),(x,2.0*scale,z),0.22*scale,(0.31,0.19,0.10))
    sphere(x,2.6*scale,z,1.25*scale,(0.10,0.34,0.15),(1.0,1.0,1.0))
    sphere(x-0.65*scale,2.35*scale,z+0.18*scale,0.82*scale,(0.13,0.40,0.18))
    sphere(x+0.62*scale,2.4*scale,z-0.12*scale,0.88*scale,(0.08,0.30,0.13))
    sphere(x,3.25*scale,z,0.78*scale,(0.15,0.43,0.20))

def draw_lamp(x,z):
    cylinder_between((x,0.15,z),(x,4.0,z),0.075,(0.18,0.20,0.22))
    cylinder_between((x,4.0,z),(x+0.75,4.0,z),0.07,(0.18,0.20,0.22))
    sphere(x+0.78,3.92,z,0.18,(1.0,0.86,0.48),shine=70)

def draw_car(x,z,color,scale=1.0):
    global wheel_angle
    # Vehicle is aligned with X axis; wheels sit outside body.
    cube(x,0.82*scale,z,3.2*scale,0.72*scale,1.45*scale,color,45)
    cube(x-0.05*scale,1.35*scale,z,1.75*scale,0.62*scale,1.18*scale,
         (0.12,0.22,0.29),65)
    # windshield side highlights
    cube(x-0.05*scale,1.36*scale,z+0.605*scale,1.48*scale,0.40*scale,0.025*scale,(0.43,0.67,0.77),50)
    cube(x-0.05*scale,1.36*scale,z-0.605*scale,1.48*scale,0.40*scale,0.025*scale,(0.43,0.67,0.77),50)
    # wheels: dark tire cylinders with silver hubs
    for wx in (x-1.0*scale,x+1.0*scale):
        for side in (-1,1):
            wz=z+side*0.74*scale
            glPushMatrix()
            glTranslatef(wx,0.48*scale,wz)
            glRotatef(90,1,0,0)
            glRotatef(wheel_angle,0,0,1)
            set_material((0.035,0.04,0.045),12)
            gluCylinder(glu,0.34*scale,0.34*scale,0.16*scale,16,1)
            set_material((0.55,0.58,0.60),45)
            gluDisk(glu,0.0,0.19*scale,16,1)
            glPopMatrix()
    # headlights and rear lamps
    for side in (-1,1):
        sphere(x+1.61*scale,0.9*scale,z+side*0.42*scale,0.12*scale,(1.0,0.92,0.62),shine=80)
        sphere(x-1.61*scale,0.9*scale,z+side*0.42*scale,0.11*scale,(0.85,0.08,0.05),shine=20)

def draw_traffic_signal(x,z):
    cylinder_between((x,0.1,z),(x,5.0,z),0.12,(0.18,0.19,0.20))
    cube(x,4.3,z,0.75,1.65,0.55,(0.08,0.09,0.10))
    active = (pygame.time.get_ticks()//2500)%3
    cols=[(0.95,0.05,0.04),(0.95,0.58,0.03),(0.04,0.75,0.18)]
    for i in range(3):
        c=cols[i] if i==active else tuple(v*0.22 for v in cols[i])
        sphere(x,4.83-i*0.52,z+0.29,0.19,c,shine=80)

def draw_scene():
    draw_ground()
    # Building blocks: carefully separated from road and from each other.
    buildings = [
        (-23, -13, 7, 7, 12, (0.58,0.62,0.66), 11),
        (-12, -14, 7, 7, 17, (0.43,0.55,0.66), 12),
        (1, -14, 8, 7, 14, (0.66,0.58,0.48), 13),
        (14, -14, 8, 7, 19, (0.48,0.58,0.62), 14),
        (25, -13, 7, 7, 11, (0.62,0.51,0.50), 15),
        (-23, 14, 7, 7, 14, (0.48,0.61,0.56), 16),
        (-5, 15, 8, 7, 12, (0.62,0.58,0.48), 17),
        (10, 15, 8, 7, 17, (0.48,0.55,0.66), 18),
        (25, 14, 7, 7, 13, (0.61,0.56,0.62), 19),
    ]
    for args in buildings:
        draw_building(*args)
    # Park trees in a spaced grid
    for x,z,s in [(-21,9,0.9),(-17,17,0.85),(-11,9,0.95),(-20,18,0.8),(-9,18,0.82)]:
        draw_tree(x,z,s)
    # Street trees along sidewalks
    for x in (-26,-18,-8,4,16,27):
        draw_tree(x,-6.4,0.72)
        draw_tree(x,6.4,0.72)
    for x in (-24,-12,0,12,24):
        draw_lamp(x,-5.3)
        draw_lamp(x,5.3)
    draw_traffic_signal(5.0,-4.0)
    # Fountain water jets
    for i in range(5):
        ang=i*2*math.pi/5
        px=-15+math.cos(ang)*0.8
        pz=13+math.sin(ang)*0.8
        cylinder_between((px,0.25,pz),(px,1.25,pz),(0.035),(0.45,0.78,0.92))
        sphere(px,1.28,pz,0.10,(0.45,0.78,0.92))
    # Animated vehicles
    draw_car(car_positions[0],-1.7,(0.72,0.08,0.06),0.95)
    draw_car(car_positions[1],1.8,(0.08,0.27,0.68),0.88)
    draw_car(car_positions[2],-1.7,(0.82,0.68,0.10),0.80)

def setup_lighting():
    if day_mode:
        ambient=(0.48,0.48,0.48,1.0)
        diffuse=(0.95,0.91,0.82,1.0)
        clear=(0.47,0.70,0.88,1.0)
    else:
        ambient=(0.20,0.22,0.32,1.0)
        diffuse=(0.48,0.54,0.72,1.0)
        clear=(0.035,0.055,0.11,1.0)
    glClearColor(*clear)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0,GL_POSITION,( -0.5,1.0,0.35,0.0))
    glLightfv(GL_LIGHT0,GL_DIFFUSE,diffuse)
    glLightfv(GL_LIGHT0,GL_SPECULAR,(0.8,0.8,0.8,1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_NORMALIZE)

def update_camera():
    yr=math.radians(yaw)
    pr=math.radians(pitch)
    cx=target[0]+distance*math.cos(pr)*math.sin(yr)
    cy=target[1]+distance*math.sin(pr)
    cz=target[2]+distance*math.cos(pr)*math.cos(yr)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(cx,cy,cz,target[0],target[1],target[2],0,1,0)

def draw_hud():
    # Pygame overlay, deliberately kept outside the 3D scene.
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0,WIDTH,HEIGHT,0,-1,1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    pygame.display.get_surface()
    # Use OpenGL bitmap text through pygame font surface.
    font=pygame.font.SysFont("arial",18,bold=True)
    lines=[
        "MODERN CITY 3D  |  COMPUTER GRAPHICS",
        "ARROWS: orbit camera   +/-: zoom   WASD: move target",
        "N: day/night   F: fog   SPACE: pause cars   ESC: exit"
    ]
    for i,line in enumerate(lines):
        surf=font.render(line,True,(245,248,252))
        raw=pygame.image.tostring(surf,"RGBA",True)
        glRasterPos2f(18,28+i*25)
        glDrawPixels(surf.get_width(),surf.get_height(),GL_RGBA,GL_UNSIGNED_BYTE,raw)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    if fog_enabled:
        glEnable(GL_FOG)

# ---------- OpenGL initialization ----------
glViewport(0,0,WIDTH,HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(48, WIDTH/HEIGHT, 0.1, 180.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)
glShadeModel(GL_SMOOTH)
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
setup_lighting()

glFogfv(GL_FOG_COLOR,(0.47,0.70,0.88,1.0))
glFogi(GL_FOG_MODE,GL_EXP2)
glFogf(GL_FOG_DENSITY,0.006)
glHint(GL_FOG_HINT,GL_NICEST)

paused=False
mouse_down=False
last_mouse=(0,0)

while running:
    dt=min(clock.tick(60)/1000.0,0.04)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE: running=False
            elif event.key==pygame.K_n:
                day_mode=not day_mode
                setup_lighting()
                glFogfv(GL_FOG_COLOR,(0.47,0.70,0.88,1.0) if day_mode else (0.035,0.055,0.11,1.0))
            elif event.key==pygame.K_f:
                fog_enabled=not fog_enabled
            elif event.key==pygame.K_SPACE:
                paused=not paused
            elif event.key in (pygame.K_EQUALS,pygame.K_PLUS,pygame.K_KP_PLUS):
                distance=max(13,distance-2)
            elif event.key in (pygame.K_MINUS,pygame.K_KP_MINUS):
                distance=min(65,distance+2)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            mouse_down=True
            last_mouse=event.pos
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
            mouse_down=False
        elif event.type==pygame.MOUSEMOTION and mouse_down:
            dx=event.pos[0]-last_mouse[0]
            dy=event.pos[1]-last_mouse[1]
            yaw += dx*0.35
            pitch=clamp(pitch-dy*0.25,8,68)
            last_mouse=event.pos
        elif event.type==pygame.MOUSEWHEEL:
            distance=clamp(distance-event.y*2,13,65)

    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: yaw-=55*dt
    if keys[pygame.K_RIGHT]: yaw+=55*dt
    if keys[pygame.K_UP]: pitch=clamp(pitch+35*dt,8,68)
    if keys[pygame.K_DOWN]: pitch=clamp(pitch-35*dt,8,68)
    move=9*dt
    if keys[pygame.K_w]: target[2]-=move
    if keys[pygame.K_s]: target[2]+=move
    if keys[pygame.K_a]: target[0]-=move
    if keys[pygame.K_d]: target[0]+=move

    if not paused:
        for i in range(len(car_positions)):
            car_positions[i]+=car_speeds[i]*dt
            if car_positions[i]>34:
                car_positions[i]=-34
        wheel_angle=(wheel_angle+220*dt)%360

    setup_lighting()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    update_camera()
    if fog_enabled: glEnable(GL_FOG)
    else: glDisable(GL_FOG)
    draw_scene()
    draw_hud()
    pygame.display.flip()

gluDeleteQuadric(glu)
pygame.quit()
sys.exit()
