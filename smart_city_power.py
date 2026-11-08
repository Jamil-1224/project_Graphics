
import pygame, math

pygame.init()
W,H = 1000,650
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Smart City Power Failure Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial",21,bold=True)
small = pygame.font.SysFont("arial",16)

# Building positions and sizes
buildings = [
    (40,300,100),(160,220,110),(290,270,100),
    (410,180,120),(550,250,100),(670,200,110),
    (810,280,100),(920,230,65)
]

power_on = True
solar_backup = False
paused = False
time_value = 0.0
running = True


def draw_text(msg,x,y,color=(255,255,255),f=font):
    screen.blit(f.render(msg,True,color),(x,y))


while running:
    dt = min(clock.tick(60)/1000,0.04)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif e.key == pygame.K_SPACE:
                paused = not paused
            elif e.key == pygame.K_1:
                power_on = not power_on
            elif e.key == pygame.K_2:
                solar_backup = not solar_backup
            elif e.key == pygame.K_r:
                power_on = True
                solar_backup = False
                time_value = 0

    if not paused:
        time_value += dt

    # Night sky
    screen.fill((12,20,45))

    # Stars
    for i in range(80):
        sx = (i*137+31)%W
        sy = (i*71+25)%300
        pygame.draw.circle(screen,(130,155,200),(sx,sy),1)

    # Moon
    pygame.draw.circle(screen,(235,235,205),(870,90),35)
    pygame.draw.circle(screen,(12,20,45),(884,78),30)

    # Ground and road
    pygame.draw.rect(screen,(35,50,60),(0,530,W,120))
    pygame.draw.rect(screen,(45,48,58),(0,565,W,85))
    for x in range(20,W,100):
        pygame.draw.rect(screen,(225,210,150),(x,605,50,4))

    # Electricity transmission poles and wires
    for px in (100,400,700,950):
        pygame.draw.line(screen,(110,125,145),(px,220),(px,530),6)
        pygame.draw.line(screen,(110,125,145),(px-25,260),(px+25,260),5)
        pygame.draw.circle(screen,(255,220,80),(px,260),5)

    # Power line: animated bright when electricity is flowing
    wire_color = (60,240,190) if power_on else (100,75,75)
    pygame.draw.lines(
        screen,wire_color,False,
        [(100,260),(250,245),(400,260),
         (550,245),(700,260),(825,245),(950,260)],3
    )

    # Energy pulse animation
    if power_on:
        pulse_x = 100 + (time_value*130)%850
        pulse_y = 250 + math.sin(pulse_x*.02)*10
        pygame.draw.circle(screen,(255,255,160),(int(pulse_x),int(pulse_y)),7)

    # City buildings
    for index,(bx,by,bw) in enumerate(buildings):
        bh = 530-by
        pygame.draw.rect(screen,(40,55,80),(bx,by,bw,bh))
        pygame.draw.rect(screen,(80,100,130),(bx,by,bw,bh),2)

        # Solar panel on selected roofs
        if index in (1,4,6):
            pygame.draw.rect(screen,(45,115,160),(bx+10,by-12,bw-20,10))
            for sx in range(bx+15,bx+bw-15,18):
                pygame.draw.line(screen,(140,215,240),(sx,by-12),(sx,by-2),1)

        # Building windows
        for wx in range(bx+12,bx+bw-8,23):
            for wy in range(by+18,520,32):
                if wy+15 < 530:
                    # Some windows are naturally unlit
                    naturally_off = (wx*3+wy*7)%6 == 0

                    if power_on or solar_backup:
                        lit = not naturally_off
                    else:
                        lit = False

                    if lit:
                        color = (255,215,105)
                    else:
                        color = (38,48,68)

                    pygame.draw.rect(screen,color,(wx,wy,11,16),border_radius=2)

    # Power status panel
    pygame.draw.rect(screen,(25,35,60),(18,18,410,160),border_radius=14)
    draw_text("SMART CITY POWER GRID",32,28,(255,220,85))

    if power_on:
        status = "GRID: ONLINE"
        status_color = (80,255,155)
    elif solar_backup:
        status = "GRID: FAILED - SOLAR BACKUP"
        status_color = (255,215,90)
    else:
        status = "GRID: POWER FAILURE"
        status_color = (255,90,90)

    draw_text(status,32,68,status_color,small)
    draw_text("1: Toggle main grid",32,98,(240,240,255),small)
    draw_text("2: Toggle solar backup",32,123,(240,240,255),small)
    draw_text("SPACE: Pause  R: Reset",32,148,(240,240,255),small)

    # Solar backup status indicator
    backup_color = (70,240,150) if solar_backup else (120,130,150)
    pygame.draw.circle(screen,backup_color,(390,130),10)

    if paused:
        draw_text("PAUSED",450,580,(255,220,80))

    pygame.display.flip()

pygame.quit()
