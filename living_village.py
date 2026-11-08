
import pygame, random, math

pygame.init()
W, H = 1000, 650
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Living Village - Weather Animation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 21, bold=True)

weather = 1  # 1 sunny, 2 cloudy, 3 rain, 4 storm
time_value = 0.0
rain = [[random.randrange(W),random.randrange(H)] for _ in range(150)]
clouds = [[80,100,18],[420,140,12],[750,95,15]]
paused = False
running = True

while running:
    dt = min(clock.tick(60)/1000,0.04)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_SPACE: paused = not paused
            if e.key == pygame.K_1: weather = 1
            if e.key == pygame.K_2: weather = 2
            if e.key == pygame.K_3: weather = 3
            if e.key == pygame.K_4: weather = 4

    if not paused:
        time_value += dt
        for c in clouds:
            c[0] += c[2]*dt
            if c[0] > W+80: c[0] = -100
        for drop in rain:
            drop[0] += (70 if weather == 4 else 20)*dt
            drop[1] += (450 if weather == 4 else 320)*dt
            if drop[1] > H:
                drop[0] = random.randrange(W)
                drop[1] = 0

    sky = [(115,195,245),(125,155,180),(75,105,135),(30,40,65)][weather-1]
    screen.fill(sky)

    # Sun or storm cloud
    if weather == 1:
        pygame.draw.circle(screen,(255,220,70),(820,110),43)
        pygame.draw.circle(screen,(255,240,150),(805,96),12)

    for x,y,speed in clouds:
        cx,cy=int(x),int(y)
        for dx,dy,r in [(-20,0,24),(10,-12,30),(40,0,24)]:
            pygame.draw.circle(screen,(100,110,125) if weather>1 else (245,248,255),(cx+dx,cy+dy),r)

    # Fields and river
    pygame.draw.rect(screen,(90,165,65),(0,300,W,185))
    pygame.draw.polygon(screen,(50,145,195),[(0,470),(280,450),(580,485),(W,455),(W,H),(0,H)])

    # House
    pygame.draw.rect(screen,(225,195,145),(150,320,140,115))
    pygame.draw.polygon(screen,(145,65,45),[(130,320),(220,260),(310,320)])
    pygame.draw.rect(screen,(95,60,40),(205,375,35,60))
    pygame.draw.rect(screen,(115,195,225),(165,345,25,25))

    # Wind-blown tree
    sway = math.sin(time_value*3)*12
    pygame.draw.line(screen,(110,70,40),(410,400),(410+sway,285),12)
    pygame.draw.circle(screen,(35,125,55),(int(410+sway),275),42)
    pygame.draw.circle(screen,(55,155,65),(int(385+sway),290),30)
    pygame.draw.circle(screen,(55,155,65),(int(435+sway),295),30)

    # Rain / storm particles
    if weather >= 3:
        for rx,ry in rain:
            pygame.draw.line(screen,(190,220,250),(int(rx),int(ry)),(int(rx-5),int(ry+12)),2)

    # Lightning flash in storm
    if weather == 4 and int(time_value*2)%9 == 0:
        pygame.draw.polygon(screen,(255,255,210),[(700,100),(670,170),(700,165),(680,230),(735,145),(705,150)])

    pygame.draw.rect(screen,(25,40,55),(15,15,360,105),border_radius=12)
    screen.blit(font.render("LIVING VILLAGE",True,(255,225,100)),(30,25))
    names = ["SUNNY DAY","CLOUDY","RAINY","THUNDERSTORM"]
    screen.blit(font.render("Weather: "+names[weather-1],True,(255,255,255)),(30,60))
    screen.blit(pygame.font.SysFont("arial",16).render("1 Sunny  2 Cloudy  3 Rain  4 Storm  SPACE Pause",True,(255,255,255)),(30,90))

    if paused:
        screen.blit(font.render("PAUSED",True,(255,255,255)),(450,570))
    pygame.display.flip()

pygame.quit()
