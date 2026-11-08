
import pygame, random

pygame.init()
W,H = 1000,650
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Smart Waste Sorting Machine")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial",22,bold=True)
small = pygame.font.SysFont("arial",16)

# Waste types and colors
types = [
    ("PLASTIC",(60,160,255)),
    ("PAPER",(240,220,160)),
    ("METAL",(180,195,210))
]
items = []
score = 0
speed = 180.0
paused = False
spawn_timer = 0.0
running = True


def spawn_item():
    name,color = random.choice(types)
    items.append({"x":-40.0,"y":340,"name":name,"color":color})


while running:
    dt = min(clock.tick(60)/1000,0.04)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: running = False
            if e.key == pygame.K_SPACE: paused = not paused
            if e.key == pygame.K_UP: speed = min(400,speed+30)
            if e.key == pygame.K_DOWN: speed = max(80,speed-30)
            if e.key == pygame.K_r:
                items = []
                score = 0
                spawn_timer = 0

    if not paused:
        spawn_timer += dt
        if spawn_timer > 1.3:
            spawn_item()
            spawn_timer = 0

        for item in items[:]:
            item["x"] += speed*dt

            # Machine automatically sorts each object into its matching bin
            if item["x"] >= 690:
                score += 1
                items.remove(item)

    screen.fill((205,225,238))

    # Background factory wall
    pygame.draw.rect(screen,(180,200,215),(0,0,W,250))
    for x in range(30,W,120):
        pygame.draw.rect(screen,(150,175,195),(x,45,75,90))

    pygame.draw.rect(screen,(40,50,65),(20,20,350,80),border_radius=12)
    screen.blit(font.render("SMART WASTE SORTER",True,(255,220,90)),(35,30))
    screen.blit(font.render(f"Sorted: {score}",True,(255,255,255)),(35,63))

    # Conveyor belt
    pygame.draw.rect(screen,(70,80,90),(30,340,690,70),border_radius=8)
    for x in range(35,720,45):
        pygame.draw.line(screen,(130,145,155),(x,345),(x,405),3)

    # Items on conveyor
    for item in items:
        x,y = int(item["x"]),item["y"]
        if item["name"] == "PLASTIC":
            pygame.draw.rect(screen,item["color"],(x,y,32,38),border_radius=5)
            pygame.draw.rect(screen,(160,220,255),(x+8,y-5,16,7))
        elif item["name"] == "PAPER":
            pygame.draw.rect(screen,item["color"],(x,y,35,28))
            pygame.draw.line(screen,(150,130,90),(x+5,y+8),(x+27,y+8),2)
        else:
            pygame.draw.rect(screen,item["color"],(x,y,32,36),border_radius=7)
            pygame.draw.ellipse(screen,(110,130,150),(x+5,y+3,22,8))

    # Sorting machine
    pygame.draw.rect(screen,(65,85,110),(680,270,70,145),border_radius=8)
    pygame.draw.rect(screen,(100,220,210),(695,285,40,24),border_radius=4)
    pygame.draw.polygon(screen,(90,105,120),[(690,415),(740,415),(780,455),(650,455)])

    # Recycling bins
    bins = [
        (760,(50,140,230),"PLASTIC"),
        (840,(215,170,70),"PAPER"),
        (920,(125,140,155),"METAL")
    ]
    for bx,color,name in bins:
        pygame.draw.rect(screen,color,(bx,465,58,100),border_radius=6)
        pygame.draw.rect(screen,(35,45,60),(bx-5,458,68,12))
        screen.blit(small.render(name,True,(25,35,45)),(bx-5,575))

    pygame.draw.rect(screen,(30,45,60),(20,605,570,32),border_radius=6)
    screen.blit(small.render("SPACE: Pause   UP/DOWN: Speed   R: Reset   ESC: Exit",True,(255,255,255)),(32,612))

    if paused:
        screen.blit(font.render("PAUSED",True,(30,45,60)),(440,200))

    pygame.display.flip()

pygame.quit()
