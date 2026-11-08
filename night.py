
import pygame
import math
import random

pygame.init()

W, H = 1000, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Day and Night City Animation")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 17)
title_font = pygame.font.SysFont("arial", 29, bold=True)

WHITE = (245, 245, 255)
YELLOW = (255, 215, 80)

running = True
paused = False
cycle_time = 0.0
speed = 1.0

# One complete day-night cycle takes 50 seconds
CYCLE_DURATION = 50.0

random.seed(21)

# Fixed city buildings
buildings = []
x = 0

while x < W:
    bw = random.randint(65, 115)
    bh = random.randint(120, 300)

    buildings.append({
        "x": x,
        "w": bw,
        "h": bh,
        "color": (
            random.randint(30, 70),
            random.randint(40, 75),
            random.randint(65, 110)
        ),
        "windows": [
            (wx, wy)
            for wx in range(12, bw - 8, 20)
            for wy in range(15, bh - 12, 25)
        ]
    })

    x += bw + 4

# Stars
stars = [
    {
        "x": random.randint(0, W),
        "y": random.randint(25, 370),
        "r": random.choice([1, 1, 2]),
        "phase": random.random() * math.tau
    }
    for _ in range(100)
]


def lerp_color(a, b, t):
    """Blend two RGB colors."""
    return tuple(
        int(a[i] + (b[i] - a[i]) * t)
        for i in range(3)
    )


def draw_text(message, x, y, color=WHITE, f=font):
    screen.blit(f.render(message, True, color), (x, y))


def day_amount():
    # 0 = midnight, 0.5 = midday, 1 = next midnight
    return (1 - math.cos(cycle_time / CYCLE_DURATION
                         * math.tau)) / 2


def draw_sky(day):
    day_color = (105, 190, 245)
    night_color = (9, 15, 42)
    sunset_color = (240, 115, 90)

    # Stronger orange light near sunrise and sunset
    sunrise = math.exp(
        -((cycle_time % CYCLE_DURATION - 12.5) / 3.0) ** 2
    )
    sunset = math.exp(
        -((cycle_time % CYCLE_DURATION - 37.5) / 3.0) ** 2
    )
    warm = min(1.0, sunrise + sunset)

    base = lerp_color(night_color, day_color, day)
    base = lerp_color(base, sunset_color, warm * (1 - day) * 0.85)

    for y in range(H):
        t = y / H
        lower = lerp_color(base, (150, 185, 210), t * 0.5)
        pygame.draw.line(screen, lower, (0, y), (W, y))


def draw_celestial_bodies(day):
    # Sun moves across the sky
    sun_angle = cycle_time / CYCLE_DURATION * math.tau - math.pi / 2
    sun_x = W / 2 + math.cos(sun_angle) * 390
    sun_y = 310 + math.sin(sun_angle) * 245

    # Moon is on the opposite side of the sky
    moon_x = W - sun_x
    moon_y = 310 - math.sin(sun_angle) * 245

    # Sun
    if day > 0.12:
        sun_alpha = int(255 * min(1, day * 3))
        sun_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(
            sun_surface, (255, 215, 70, sun_alpha),
            (50, 50), 32
        )
        screen.blit(sun_surface, (int(sun_x - 50), int(sun_y - 50)))

    # Moon and stars become visible at night
    if day < 0.55:
        moon_alpha = int(255 * (1 - day / 0.55))
        moon_surface = pygame.Surface((90, 90), pygame.SRCALPHA)

        pygame.draw.circle(
            moon_surface, (225, 230, 245, moon_alpha),
            (45, 45), 27
        )
        pygame.draw.circle(
            moon_surface, (20, 30, 60, moon_alpha),
            (56, 36), 25
        )
        screen.blit(moon_surface, (int(moon_x - 45), int(moon_y - 45)))

        for star in stars:
            twinkle = (math.sin(cycle_time * 3 + star["phase"]) + 1) / 2
            brightness = int(100 + 155 * twinkle)
            brightness = int(brightness * (1 - day / 0.55))

            if brightness > 0:
                pygame.draw.circle(
                    screen,
                    (brightness, brightness, min(255, brightness + 10)),
                    (star["x"], star["y"]), star["r"]
                )


def draw_city(day):
    ground_y = 510

    # City ground
    pygame.draw.rect(
        screen, (43, 65, 75),
        (0, ground_y, W, H - ground_y)
    )

    night_factor = 1 - day

    for building in buildings:
        bx = building["x"]
        bw = building["w"]
        bh = building["h"]
        by = ground_y - bh

        # Building becomes brighter in daytime
        daylight_color = lerp_color(
            building["color"],
            (110, 130, 150),
            day * 0.65
        )

        pygame.draw.rect(
            screen, daylight_color,
            (bx, by, bw, bh)
        )

        # Building roof
        pygame.draw.line(
            screen, (150, 165, 185),
            (bx, by), (bx + bw, by), 3
        )

        # Windows glow at night
        for wx, wy in building["windows"]:
            if wy + 10 >= bh:
                continue

            window_x = bx + wx
            window_y = by + wy

            if night_factor > 0.30:
                lit = (wx * 7 + wy * 11 + int(cycle_time)) % 5 != 0

                if lit:
                    window_color = lerp_color(
                        (50, 65, 90),
                        (255, 210, 100),
                        night_factor
                    )
                else:
                    window_color = (50, 65, 90)
            else:
                window_color = (180, 215, 235)

            pygame.draw.rect(
                screen, window_color,
                (window_x, window_y, 9, 13),
                border_radius=2
            )

    # Road
    pygame.draw.rect(
        screen, (42, 46, 55),
        (0, 565, W, 85)
    )

    for rx in range(20, W, 95):
        pygame.draw.rect(
            screen, (235, 215, 145),
            (rx, 605, 48, 4)
        )


def draw_street_lights(day):
    night = 1 - day

    # Lights glow only when it is dark
    for lx in (120, 330, 560, 790, 940):
        pygame.draw.line(
            screen, (80, 85, 95),
            (lx, 565), (lx, 485), 6
        )
        pygame.draw.line(
            screen, (80, 85, 95),
            (lx, 485), (lx + 20, 470), 5
        )

        light_color = lerp_color(
            (190, 205, 215),
            (255, 220, 110),
            night
        )

        pygame.draw.circle(
            screen, light_color,
            (lx + 20, 470), 8
        )

        if night > 0.25:
            glow = pygame.Surface((100, 100), pygame.SRCALPHA)
            alpha = int(55 * night)
            pygame.draw.circle(
                glow, (255, 210, 100, alpha),
                (50, 50), 35
            )
            screen.blit(glow, (lx - 30, 420))


def draw_dashboard(day):
    pygame.draw.rect(
        screen, (25, 35, 55),
        (18, 18, 330, 110),
        border_radius=12
    )

    draw_text(
        "DAY & NIGHT CITY",
        32, 28, YELLOW, title_font
    )

    if day > 0.65:
        phase = "DAYTIME"
    elif day > 0.35:
        phase = "SUNRISE / SUNSET"
    else:
        phase = "NIGHTTIME"

    draw_text("Phase: " + phase, 32, 70)
    draw_text(f"Daylight: {day * 100:.0f}%", 32, 96)


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
                cycle_time = 0.0
                speed = 1.0

    if not paused:
        cycle_time += dt * speed

    day = day_amount()

    draw_sky(day)
    draw_celestial_bodies(day)
    draw_city(day)
    draw_street_lights(day)
    draw_dashboard(day)

    draw_text(
        "SPACE: Pause   UP/DOWN: Speed   R: Reset   ESC: Exit",
        205, 665
    )

    if paused:
        draw_text("PAUSED", 440, 570, YELLOW, title_font)

    pygame.display.flip()

pygame.quit()
