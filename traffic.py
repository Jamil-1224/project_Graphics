
import pygame
import math

pygame.init()

W, H = 1000, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Smart Traffic System")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 19, bold=True)
small = pygame.font.SysFont("arial", 15)
title_font = pygame.font.SysFont("arial", 29, bold=True)

BG = (190, 225, 245)
ROAD = (49, 56, 68)
WHITE = (245, 248, 250)
GREEN = (48, 190, 100)
RED = (240, 65, 75)
YELLOW = (255, 200, 50)
DARK = (25, 32, 43)

road_y = 300
road_h = 180
stop_x = 700

cars = []
paused = False
running = True
elapsed = 0.0
ped_x = 620.0
ped_direction = 1
ped_wait = 0.0


def reset():
    global cars, elapsed, ped_x, ped_direction, ped_wait
    cars = [
        {"x": -130.0, "y": 335, "speed": 180, "color": (60, 150, 255)},
        {"x": -420.0, "y": 405, "speed": 155, "color": (255, 130, 70)},
        {"x": -760.0, "y": 335, "speed": 170, "color": (180, 110, 240)},
    ]
    elapsed = 0.0
    ped_x = 620.0
    ped_direction = 1
    ped_wait = 0.0


def text(msg, x, y, color=WHITE, f=font):
    screen.blit(f.render(msg, True, color), (x, y))


def draw_car(car):
    x, y = int(car["x"]), car["y"]
    color = car["color"]

    # Shadow and body
    pygame.draw.rect(screen, (25, 30, 38),
                     (x + 3, y + 8, 100, 34), border_radius=9)
    pygame.draw.rect(screen, color,
                     (x, y, 100, 34), border_radius=9)

    # Windows
    pygame.draw.polygon(screen, (190, 230, 245), [
        (x + 23, y + 3), (x + 64, y + 3),
        (x + 76, y + 15), (x + 18, y + 15)
    ])

    # Wheels
    for wx in (x + 20, x + 76):
        pygame.draw.circle(screen, DARK, (wx, y + 33), 10)
        pygame.draw.circle(screen, (175, 185, 195), (wx, y + 33), 4)

    pygame.draw.rect(screen, (255, 245, 190),
                     (x + 91, y + 8, 6, 7), border_radius=2)


def draw_person(x, y):
    pygame.draw.circle(screen, (240, 190, 145), (int(x), int(y - 21)), 8)
    pygame.draw.line(screen, (55, 105, 220),
                     (int(x), int(y - 13)), (int(x), int(y + 8)), 5)
    swing = math.sin(elapsed * 8) * 8
    pygame.draw.line(screen, DARK,
                     (int(x), int(y + 6)),
                     (int(x - 7 + swing), int(y + 19)), 4)
    pygame.draw.line(screen, DARK,
                     (int(x), int(y + 6)),
                     (int(x + 7 - swing), int(y + 19)), 4)
    pygame.draw.line(screen, (240, 190, 145),
                     (int(x), int(y - 8)),
                     (int(x - 10 - swing), int(y + 1)), 4)
    pygame.draw.line(screen, (240, 190, 145),
                     (int(x), int(y - 8)),
                     (int(x + 10 + swing), int(y + 1)), 4)


def draw_scene():
    screen.fill(BG)

    # Grass strips
    pygame.draw.rect(screen, (120, 190, 105), (0, 220, W, 80))
    pygame.draw.rect(screen, (120, 190, 105), (0, 480, W, 170))

    # Road
    pygame.draw.rect(screen, ROAD, (0, road_y, W, road_h))

    # Road edges
    pygame.draw.line(screen, WHITE, (0, road_y), (W, road_y), 4)
    pygame.draw.line(screen, WHITE, (0, road_y + road_h),
                     (W, road_y + road_h), 4)

    # Lane divider
    for x in range(0, W, 70):
        pygame.draw.rect(screen, (225, 225, 210),
                         (x, 387, 38, 4))

    # Zebra crossing
    for y in range(road_y + 8, road_y + road_h - 8, 22):
        pygame.draw.rect(screen, WHITE, (605, y, 65, 12))

    # Sidewalk
    pygame.draw.rect(screen, (205, 205, 195), (0, 480, W, 25))

    # Trees
    for tx in (70, 190, 870, 950):
        pygame.draw.rect(screen, (120, 80, 45),
                         (tx - 5, 255, 10, 35))
        pygame.draw.circle(screen, (40, 145, 75), (tx, 245), 24)

    # Traffic light pole
    pygame.draw.rect(screen, (100, 110, 120), (755, 220, 9, 80))
    pygame.draw.rect(screen, (35, 40, 48), (730, 155, 58, 115),
                     border_radius=12)

    # Signal phases: green 0-7, yellow 7-9, red 9-15
    phase = elapsed % 15
    if phase < 7:
        signal = "GREEN"
        active = GREEN
        remaining = 7 - phase
    elif phase < 9:
        signal = "YELLOW"
        active = YELLOW
        remaining = 9 - phase
    else:
        signal = "RED"
        active = RED
        remaining = 15 - phase

    signal_colors = {
        "RED": RED if signal == "RED" else (90, 45, 50),
        "YELLOW": YELLOW if signal == "YELLOW" else (90, 78, 40),
        "GREEN": GREEN if signal == "GREEN" else (40, 85, 58)
    }

    for i, name in enumerate(("RED", "YELLOW", "GREEN")):
        pygame.draw.circle(screen, signal_colors[name],
                           (759, 178 + i * 35), 12)

    # Stop line
    pygame.draw.line(screen, YELLOW, (stop_x, 300),
                     (stop_x, 480), 4)

    return signal, remaining


def draw_panel(signal, remaining):
    pygame.draw.rect(screen, (27, 43, 62),
                     (20, 20, 340, 125), border_radius=14)
    text("SMART TRAFFIC SYSTEM", 38, 33, YELLOW, title_font)
    text("Signal: " + signal, 38, 76, WHITE)
    text("Next change: " + str(max(0, math.ceil(remaining))) + " sec",
         38, 106, WHITE, small)


reset()

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
            elif event.key == pygame.K_r:
                reset()

    if not paused:
        elapsed += dt

    signal, remaining = draw_scene()

    if not paused:
        # Cars stop before the stop line when signal is red/yellow
        for car in cars:
            next_x = car["x"] + car["speed"] * dt
            front = next_x + 100

            if signal != "GREEN" and car["x"] < stop_x:
                if front >= stop_x - 8:
                    next_x = stop_x - 108

            # Keep cars from overlapping each other in the same lane
            car["x"] = next_x

            if car["x"] > W + 20:
                car["x"] = -130.0  # replaced below

        # Pedestrian crosses during red signal
        if signal == "RED":
            ped_x += 65 * dt * ped_direction
            if ped_x > 680:
                ped_direction = -1
            elif ped_x < 590:
                ped_direction = 1

    for car in cars:
        draw_car(car)

    if signal == "RED":
        draw_person(ped_x, 500)

    draw_panel(signal, remaining)

    text("SPACE: Pause   R: Reset   ESC: Exit",
         625, 25, DARK, small)

    if paused:
        text("PAUSED", 450, 570, DARK, title_font)

    pygame.display.flip()

pygame.quit()
