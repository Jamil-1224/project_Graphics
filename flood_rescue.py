
import pygame, random, math

pygame.init()
W, H = 1000, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flood Rescue Mission")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22, bold=True)

boat_x = 100.0
water = 470.0
rescued = 0
paused = False
people = [[260, 435], [500, 410], [800, 445]]
rain = [[random.randrange(W), random.randrange(H)] for _ in range(100)]
running = True

while running:
    dt = min(clock.tick(60) / 1000, 0.04)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_SPACE: paused = not paused
            if e.key == pygame.K_r:
                boat_x, water, rescued = 100.0, 470.0, 0
                people = [[260,435],[500,410],[800,445]]

    keys = pygame.key.get_pressed()
    if not paused:
        water = min(530, water + 1.0 * dt)
        if keys[pygame.K_LEFT]: boat_x -= 220 * dt
        if keys[pygame.K_RIGHT]: boat_x += 220 * dt
        boat_x = max(0, min(W - 150, boat_x))

        for drop in rain:
            drop[1] += 350 * dt
            if drop[1] > H:
                drop[0], drop[1] = random.randrange(W), 0

        for p in people[:]:
            if keys[pygame.K_SPACE] and abs(boat_x + 65 - p[0]) < 65:
                people.remove(p)
                rescued += 1

    # Sky and rain
    screen.fill((105, 155, 190))
    pygame.draw.rect(screen, (70, 125, 75), (0, 330, W, 90))

    # Flood water
    pygame.draw.rect(screen, (35, 130, 200), (0, int(water), W, H))
    for x in range(0, W, 70):
        yy = int(water + 20 + math.sin(x * .04 + pygame.time.get_ticks() * .003)*5)
        pygame.draw.arc(screen, (110, 220, 240), (x, yy, 45, 12), 0, math.pi, 2)

    # Houses
    for x in (100, 390, 700):
        pygame.draw.rect(screen, (215, 190, 145), (x, 300, 115, 100))
        pygame.draw.polygon(screen, (115, 65, 45), [(x-10,300),(x+55,250),(x+125,300)])
        pygame.draw.rect(screen, (90, 60, 40), (x+45,345,25,55))

    for drop in rain:
        pygame.draw.line(screen, (190, 225, 255), drop, (drop[0]-4, drop[1]+10), 2)

    # People waiting for rescue
    for px, py in people:
        pygame.draw.circle(screen, (245, 190, 145), (px, py-22), 9)
        pygame.draw.line(screen, (240, 210, 80), (px, py-13), (px, py+13), 8)
        pygame.draw.line(screen, (245, 190, 145), (px, py-8), (px-12, py-18), 4)
        pygame.draw.line(screen, (245, 190, 145), (px, py-8), (px+12, py-18), 4)

    # Rescue boat
    by = int(water - 35 + math.sin(pygame.time.get_ticks()*.004)*3)
    pygame.draw.polygon(screen, (100, 50, 30), [(int(boat_x),by),(int(boat_x+135),by),(int(boat_x+115),by+28),(int(boat_x+18),by+28)])
    pygame.draw.circle(screen, (240, 190, 140), (int(boat_x+65),by-10), 10)
    pygame.draw.rect(screen, (30, 90, 70), (int(boat_x+55),by,22,13))

    pygame.draw.rect(screen, (20, 35, 55), (15, 15, 390, 80), border_radius=12)
    screen.blit(font.render("FLOOD RESCUE MISSION", True, (255,220,90)), (28,25))
    screen.blit(font.render(f"Rescued: {rescued}/{3}  Water: {int(water)}", True, (255,255,255)), (28,57))
    screen.blit(font.render("LEFT/RIGHT: Move   SPACE: Rescue   R: Reset", True, (255,255,255)), (230,610))

    if paused:
        screen.blit(font.render("PAUSED", True, (255,255,255)), (450, 300))
    pygame.display.flip()

pygame.quit()
