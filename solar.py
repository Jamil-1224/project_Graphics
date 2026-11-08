
import pygame
import math
import random

pygame.init()

W, H = 1000, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Solar System Animation")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 30, bold=True)

SPACE = (8, 12, 32)
WHITE = (235, 240, 255)
YELLOW = (255, 200, 55)

cx, cy = W // 2, H // 2 + 20
running = True
paused = False
time_value = 0.0
speed = 1.0

# Name, orbit radius, planet radius, color, orbital period (relative)
planets = [
    ("Mercury", 65, 5, (175, 170, 165), 0.24),
    ("Venus", 100, 9, (235, 180, 100), 0.62),
    ("Earth", 140, 10, (65, 145, 255), 1.00),
    ("Mars", 180, 8, (230, 95, 70), 1.88),
    ("Jupiter", 235, 19, (215, 170, 125), 3.20),
    ("Saturn", 295, 16, (225, 205, 140), 4.80),
    ("Uranus", 350, 12, (105, 220, 220), 6.80),
    ("Neptune", 400, 12, (70, 105, 245), 9.50),
]

random.seed(12)
stars = [
    (random.randrange(W), random.randrange(H),
     random.choice([1, 1, 2]))
    for _ in range(180)
]


def draw_text(message, x, y, color=WHITE, f=font):
    screen.blit(f.render(message, True, color), (x, y))


def draw_background():
    screen.fill(SPACE)
    for sx, sy, radius in stars:
        pygame.draw.circle(screen, (140, 155, 190),
                           (sx, sy), radius)


def draw_sun():
    # Soft glow
    for radius, color in [
        (48, (75, 48, 25)),
        (39, (150, 100, 35)),
        (30, (255, 155, 30)),
        (23, (255, 205, 60)),
    ]:
        pygame.draw.circle(screen, color, (cx, cy), radius)


def planet_position(index, orbit_radius, period):
    # Different angular speeds produce different revolution times
    angle = time_value * 0.55 / period + index * 0.7

    px = cx + math.cos(angle) * orbit_radius
    py = cy + math.sin(angle) * orbit_radius * 0.68

    return int(px), int(py)


def draw_planet(name, px, py, radius, color):
    # Saturn's rings
    if name == "Saturn":
        pygame.draw.ellipse(
            screen, (175, 155, 105),
            (px - radius - 10, py - 6,
             radius * 2 + 20, 12), 3
        )

    # Planet body
    pygame.draw.circle(screen, color, (px, py), radius)

    # Highlight
    if radius > 6:
        pygame.draw.circle(
            screen,
            tuple(min(255, c + 35) for c in color),
            (px - radius // 3, py - radius // 3),
            max(2, radius // 3)
        )

    # Earth: a tiny moon
    if name == "Earth":
        moon_angle = time_value * 2.2
        mx = px + int(math.cos(moon_angle) * 17)
        my = py + int(math.sin(moon_angle) * 13)
        pygame.draw.circle(screen, (200, 210, 220), (mx, my), 3)


def draw_dashboard():
    pygame.draw.rect(
        screen, (22, 28, 55),
        (15, 15, 335, 110), border_radius=12
    )
    draw_text("SOLAR SYSTEM", 30, 25, YELLOW, title_font)
    draw_text("Eight planets orbit the Sun", 30, 65)
    draw_text(f"Animation speed: {speed:.1f}x", 30, 92)


while running:
    dt = min(clock.tick(60) / 1000, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                speed = min(3.0, speed + 0.2)
            elif event.key == pygame.K_DOWN:
                speed = max(0.2, speed - 0.2)
            elif event.key == pygame.K_r:
                time_value = 0.0
                speed = 1.0

    if not paused:
        time_value += dt * speed

    draw_background()

    # Orbit paths
    for name, orbit, radius, color, period in planets:
        pygame.draw.ellipse(
            screen, (55, 65, 95),
            (cx - orbit, cy - orbit * 0.68,
             orbit * 2, orbit * 1.36), 1
        )

    draw_sun()

    # Planets and labels
    for index, (name, orbit, radius, color, period) in enumerate(planets):
        px, py = planet_position(index, orbit, period)
        draw_planet(name, px, py, radius, color)

        draw_text(name, px + radius + 4, py - 8,
                  (205, 215, 235))

    draw_dashboard()

    draw_text("SPACE: Pause   UP/DOWN: Speed   R: Reset   ESC: Exit",
              165, 665)

    if paused:
        draw_text("PAUSED", 450, 615, YELLOW, title_font)

    pygame.display.flip()

pygame.quit()
