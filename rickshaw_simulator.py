
import pygame, math, random

pygame.init()
W, H = 1000, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Dhaka Rickshaw Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 23, bold=True)

rx, ry = 180.0, 440.0
road_offset = 0.0
score = 0
obstacles = [[750.0, 450], [1200.0, 510], [1600.0, 430]]
running = True
paused = False

while running:
    dt = min(clock.tick(60)/1000, 0.04)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_SPACE: paused = not paused
            if e.key == pygame.K_r:
                rx, ry, score, road_offset = 180.0, 440.0, 0, 0.0
                obstacles = [[750.0,450],[1200.0,510],[1600.0,430]]

    keys = pygame.key.get_pressed()
    if not paused:
        if keys[pygame.K_LEFT]: rx -= 230*dt
        if keys[pygame.K_RIGHT]: rx += 230*dt
        if keys[pygame.K_UP]: ry -= 180*dt
        if keys[pygame.K_DOWN]: ry += 180*dt
        rx = max(20, min(W-150, rx))
        ry = max(350, min(520, ry))
        road_offset = (road_offset + 240*dt) % 80

        for ob in obstacles:
            ob[0] -= 240*dt
            if ob[0] < -40:
                ob[0] = W + random.randint(150, 400)
                ob[1] = random.choice([390, 450, 500])
                score += 1

    # Sky and city
    screen.fill((140, 210, 245))
    pygame.draw.rect(screen, (100,180,95), (0,280,W,100))
    for i in range(8):
        bx = i*140
        pygame.draw.rect(screen, (175,185,200), (bx, 170, 90, 140))
        for wx in range(bx+12, bx+80, 24):
            for wy in range(185, 285, 30):
                pygame.draw.rect(screen, (245,220,130), (wx,wy,10,14))

    # Road
    pygame.draw.rect(screen, (55,58,65), (0,320,W,330))
    for x in range(-80, W+80, 100):
        pygame.draw.rect(screen, (240,235,205), (x-int(road_offset), 600, 55, 5))

    # Puddles
    for x in (100, 420, 820):
        pygame.draw.ellipse(screen, (90,150,175), (x, 570, 65, 12))

    # Obstacles
    for ox, oy in obstacles:
        pygame.draw.rect(screen, (210,75,60), (int(ox),oy,32,38), border_radius=5)
        pygame.draw.circle(screen, (250,230,170), (int(ox+16),oy+8), 4)

    # Rickshaw body and decorative canopy
    pygame.draw.circle(screen, (25,30,35), (int(rx+25),int(ry+65)), 18)
    pygame.draw.circle(screen, (25,30,35), (int(rx+110),int(ry+65)), 18)
    pygame.draw.circle(screen, (190,195,200), (int(rx+25),int(ry+65)), 8)
    pygame.draw.circle(screen, (190,195,200), (int(rx+110),int(ry+65)), 8)
    pygame.draw.line(screen, (170,210,230), (int(rx+25),int(ry+65)), (int(rx+65),int(ry+25)), 5)
    pygame.draw.line(screen, (170,210,230), (int(rx+110),int(ry+65)), (int(rx+65),int(ry+25)), 5)
    pygame.draw.polygon(screen, (220,65,75), [(int(rx+30),int(ry+25)),(int(rx+50),int(ry-5)),(int(rx+100),int(ry-5)),(int(rx+120),int(ry+25))])
    pygame.draw.line(screen, (245,205,65), (int(rx+25),int(ry+65)), (int(rx+110),int(ry+65)), 5)
    pygame.draw.circle(screen, (230,175,125), (int(rx+75),int(ry+12)), 10)
    pygame.draw.line(screen, (30,90,160), (int(rx+75),int(ry+22)), (int(rx+75),int(ry+50)), 8)

    # Collision detection
    hit = any(abs(rx+70-ox) < 40 and abs(ry+40-oy) < 40 for ox,oy in obstacles)
    if hit:
        pygame.draw.rect(screen, (120,20,20), (250,30,500,60), border_radius=10)
        screen.blit(font.render("OBSTACLE! Move to avoid it!", True, (255,255,255)), (285,45))

    pygame.draw.rect(screen, (25,35,55), (15,15,280,70), border_radius=12)
    screen.blit(font.render("DHAKA RICKSHAW", True, (255,220,80)), (28,23))
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (28,53))
    screen.blit(font.render("ARROWS: Move   SPACE: Pause   R: Reset", True, (255,255,255)), (300,615))

    if paused:
        screen.blit(font.render("PAUSED", True, (255,255,255)), (450,280))
    pygame.display.flip()

pygame.quit()
