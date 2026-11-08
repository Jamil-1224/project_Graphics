
import pygame, random, math

pygame.init()
W,H = 1000,650
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Interactive Fisherman Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial",22,bold=True)

boat_x = 100.0
fish = []
for i in range(8):
    fish.append({
        "x":random.randint(30,W-30),
        "y":random.randint(410,590),
        "speed":random.choice([-1,1])*random.randint(35,90),
        "color":random.choice([(255,150,75),(255,210,80),(100,230,200)])
    })

net_active = False
net_time = 0.0
score = 0
paused = False
running = True

while running:
    dt = min(clock.tick(60)/1000,0.04)

    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_SPACE and not paused:
                net_active = True
                net_time = 0.7
            if e.key == pygame.K_p: paused = not paused
            if e.key == pygame.K_r:
                boat_x = 100.0
                score = 0
                net_active = False

    keys = pygame.key.get_pressed()

    if not paused:
        if keys[pygame.K_LEFT]: boat_x -= 200*dt
        if keys[pygame.K_RIGHT]: boat_x += 200*dt
        boat_x = max(0,min(W-150,boat_x))

        for f in fish:
            f["x"] += f["speed"]*dt
            if f["x"] < 15 or f["x"] > W-15:
                f["speed"] *= -1

        if net_active:
            net_time -= dt
            for f in fish[:]:
                if abs(f["x"]-(boat_x+65)) < 75 and abs(f["y"]-510) < 75:
                    fish.remove(f)
                    score += 1
                    fish.append({
                        "x":random.randint(20,W-20),
                        "y":random.randint(420,590),
                        "speed":random.choice([-1,1])*random.randint(35,90),
                        "color":random.choice([(255,150,75),(255,210,80),(100,230,200)])
                    })
            if net_time <= 0:
                net_active = False

    # Sky and village banks
    screen.fill((115,200,240))
    pygame.draw.circle(screen,(255,220,70),(840,95),38)
    pygame.draw.rect(screen,(80,165,75),(0,220,W,70))
    for x in (80,260,750,920):
        pygame.draw.rect(screen,(120,75,40),(x,180,12,80))
        pygame.draw.circle(screen,(35,125,55),(x+5,170),35)

    # River
    pygame.draw.rect(screen,(35,135,200),(0,290,W,H-290))
    for x in range(0,W,80):
        pygame.draw.arc(screen,(100,210,235),(x,325,45,14),0,math.pi,2)

    # Fish
    for f in fish:
        x,y = int(f["x"]),int(f["y"])
        pygame.draw.ellipse(screen,f["color"],(x-13,y-7,26,14))
        pygame.draw.polygon(screen,f["color"],[(x-12,y),(x-22,y-8),(x-22,y+8)])
        pygame.draw.circle(screen,(20,30,40),(x+6,y-2),2)

    # Boat
    by = 355 + math.sin(pygame.time.get_ticks()*.004)*3
    pygame.draw.polygon(screen,(100,55,30),[(int(boat_x),by),(int(boat_x+145),by),(int(boat_x+120),by+30),(int(boat_x+20),by+30)])
    pygame.draw.circle(screen,(235,175,125),(int(boat_x+65),int(by-12)),10)
    pygame.draw.line(screen,(40,100,70),(int(boat_x+65),int(by-2)),(int(boat_x+65),int(by+20)),8)

    # Fishing net
    if net_active:
        nx,ny = int(boat_x+65),int(by+80)
        pygame.draw.line(screen,(240,235,210),(int(boat_x+65),int(by+20)),(nx,ny),3)
        pygame.draw.circle(screen,(240,235,210),(nx,ny),42,3)
        for offset in (-20,0,20):
            pygame.draw.line(screen,(240,235,210),(nx-25,ny+offset),(nx+25,ny+offset),1)

    pygame.draw.rect(screen,(25,40,60),(15,15,350,80),border_radius=12)
    screen.blit(font.render("FISHERMAN SIMULATOR",True,(255,220,80)),(28,25))
    screen.blit(font.render(f"Fish caught: {score}",True,(255,255,255)),(28,58))
    screen.blit(pygame.font.SysFont("arial",17).render("LEFT/RIGHT: Boat   SPACE: Cast net   P: Pause   R: Reset",True,(255,255,255)),(220,615))

    if paused:
        screen.blit(font.render("PAUSED",True,(255,255,255)),(450,270))

    pygame.display.flip()

pygame.quit()
