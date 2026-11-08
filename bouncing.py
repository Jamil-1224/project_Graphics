
import math
import random
import pygame

# -------------------- INITIALIZATION --------------------
pygame.init()

WIDTH, HEIGHT = 1000, 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Physics Animation")
clock = pygame.time.Clock()

# Colors
BG = (15, 24, 43)
WHITE = (240, 245, 255)
CYAN = (60, 220, 240)
BLUE = (45, 110, 220)
FLOOR = (90, 115, 145)
PANEL = (27, 40, 65)
MUTED = (160, 180, 205)

font = pygame.font.SysFont("consolas", 19)
small_font = pygame.font.SysFont("consolas", 15)
title_font = pygame.font.SysFont("consolas", 30, bold=True)

# -------------------- PHYSICS SETTINGS --------------------
RADIUS = 28
FLOOR_Y = 550
GRAVITY = 1100.0       # pixels per second squared
RESTITUTION = 0.78     # energy retained after bounce
INITIAL_SPEED = 650.0  # initial upward speed

# Ball state
x = WIDTH / 2
y = 150.0
vx = 180.0
vy = 0.0

speed_multiplier = 1.0
bounce_count = 0
paused = False
trail = []
particles = []
running = True


def reset_ball():
    global x, y, vx, vy, bounce_count, trail, particles
    x = WIDTH / 2
    y = 150.0
    vx = 180.0
    vy = 0.0
    bounce_count = 0
    trail = []
    particles = []


def draw_text(text, x_pos, y_pos, color=WHITE, font_obj=font):
    image = font_obj.render(text, True, color)
    screen.blit(image, (x_pos, y_pos))


def create_particles():
    for _ in range(14):
        particles.append({
            "x": x + random.uniform(-RADIUS, RADIUS),
            "y": FLOOR_Y,
            "vx": random.uniform(-160, 160),
            "vy": random.uniform(-260, -60),
            "life": random.uniform(0.25, 0.55)
        })


def draw_background():
    screen.fill(BG)

    # Subtle background grid
    for gx in range(0, WIDTH, 50):
        pygame.draw.line(screen, (24, 37, 60),
                         (gx, 0), (gx, HEIGHT), 1)

    for gy in range(0, HEIGHT, 50):
        pygame.draw.line(screen, (24, 37, 60),
                         (0, gy), (WIDTH, gy), 1)

    # Ground
    pygame.draw.rect(
        screen, (32, 48, 70),
        (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y)
    )
    pygame.draw.line(
        screen, CYAN, (0, FLOOR_Y), (WIDTH, FLOOR_Y), 3
    )


def draw_ball():
    # Ball shadow: becomes wider when the ball is higher
    height_above_floor = max(0, FLOOR_Y - y - RADIUS)
    shadow_width = max(22, int(100 - height_above_floor * 0.12))
    shadow_rect = pygame.Rect(
        int(x - shadow_width / 2),
        FLOOR_Y + 9,
        shadow_width,
        10
    )
    pygame.draw.ellipse(screen, (8, 14, 27), shadow_rect)

    # Motion trail
    for i, point in enumerate(trail):
        ratio = (i + 1) / max(1, len(trail))
        trail_radius = max(2, int(RADIUS * ratio * 0.65))
        trail_color = (
            int(30 + 30 * ratio),
            int(90 + 100 * ratio),
            int(150 + 90 * ratio)
        )
        pygame.draw.circle(
            screen, trail_color,
            (int(point[0]), int(point[1])), trail_radius
        )

    # Main ball with gradient-like concentric circles
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), RADIUS)
    pygame.draw.circle(
        screen, (70, 160, 245),
        (int(x - 5), int(y - 6)), RADIUS - 7
    )
    pygame.draw.circle(
        screen, CYAN,
        (int(x - 9), int(y - 11)), 6
    )
    pygame.draw.circle(
        screen, WHITE,
        (int(x - 10), int(y - 12)), 2
    )


def draw_dashboard():
    pygame.draw.rect(
        screen, PANEL, (20, 20, 335, 190), border_radius=12
    )

    draw_text("BOUNCING BALL LAB", 38, 35, CYAN, title_font)
    draw_text(f"Position Y : {y:7.1f} px", 38, 82)
    draw_text(f"Velocity Y : {vy:7.1f} px/s", 38, 111)
    draw_text(f"Gravity    : {GRAVITY:.0f} px/s^2", 38, 140)
    draw_text(f"Bounces    : {bounce_count}", 38, 169)

    # Instructions panel
    pygame.draw.rect(
        screen, PANEL, (WIDTH - 300, 20, 280, 190),
        border_radius=12
    )
    draw_text("CONTROLS", WIDTH - 278, 35, CYAN, title_font)
    draw_text("[SPACE] Pause / Resume", WIDTH - 278, 82, WHITE, small_font)
    draw_text("[R] Reset ball", WIDTH - 278, 108, WHITE, small_font)
    draw_text("[UP/DOWN] Speed", WIDTH - 278, 134, WHITE, small_font)
    draw_text("[ESC] Exit", WIDTH - 278, 160, WHITE, small_font)
    draw_text(
        f"Speed: {speed_multiplier:.1f}x",
        WIDTH - 278, 183, CYAN, small_font
    )


def draw_particles():
    for particle in particles:
        pygame.draw.circle(
            screen, CYAN,
            (int(particle["x"]), int(particle["y"])), 3
        )


# -------------------- MAIN ANIMATION LOOP --------------------
while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.033)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                reset_ball()
            elif event.key == pygame.K_UP:
                speed_multiplier = min(2.0, speed_multiplier + 0.1)
            elif event.key == pygame.K_DOWN:
                speed_multiplier = max(0.2, speed_multiplier - 0.1)

    # Update physics only when not paused
    if not paused:
        step = dt * speed_multiplier

        # Gravity changes vertical velocity
        vy += GRAVITY * step

        # Update position
        x += vx * step
        y += vy * step

        # Horizontal wall collision
        if x - RADIUS < 0:
            x = RADIUS
            vx = abs(vx)
        elif x + RADIUS > WIDTH:
            x = WIDTH - RADIUS
            vx = -abs(vx)

        # Floor collision and bouncing
        if y + RADIUS >= FLOOR_Y:
            y = FLOOR_Y - RADIUS

            if vy > 0:
                impact_speed = vy
                bounce_count += 1
                create_particles()

                # Reverse velocity and lose energy
                vy = -vy * RESTITUTION

                # Stop tiny bounces
                if abs(vy) < 65:
                    vy = 0.0
                    vx *= 0.90

        # Update motion trail
        trail.append((x, y))
        if len(trail) > 12:
            trail.pop(0)

        # Update impact particles
        for particle in particles[:]:
            particle["life"] -= step
            particle["vy"] += GRAVITY * 0.5 * step
            particle["x"] += particle["vx"] * step
            particle["y"] += particle["vy"] * step

            if particle["life"] <= 0:
                particles.remove(particle)

    # Render scene
    draw_background()
    draw_particles()
    draw_ball()
    draw_dashboard()

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        screen.blit(overlay, (0, 0))

        message = title_font.render("PAUSED", True, WHITE)
        screen.blit(
            message,
            (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 25)
        )

    pygame.display.flip()

pygame.quit()
