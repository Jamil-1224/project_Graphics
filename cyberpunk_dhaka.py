import pygame, random, math, sys
pygame.init()
W,H=1100,680
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("Cyberpunk Dhaka - Computer Graphics Project")
clock=pygame.time.Clock()
font=pygame.font.SysFont("consolas",20,bold=True)
small=pygame.font.SysFont("consolas",14)
rain=[[random.randrange(W),random.randrange(H),random.randrange(5,13)] for _ in range(180)]
cars=[[-200,500,random.choice([(0,240,255),(255,40,180),(255,210,60)])] for _ in range(4)]
buildings=[]
x=0
while x<W:
    bw=random.randint(65,115); bh=random.randint(150,330)
    buildings.append((x,bw,bh))
    x+=bw+8
stars=[(random.randrange(W),random.randrange(40,300)) for _ in range(70)]
t=0; running=True
while running:
    dt=clock.tick(60)/1000; t+=dt
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
    screen.fill((7,9,28))
    for sx,sy in stars: pygame.draw.circle(screen,(100,130,180),(sx,sy),1)
    # moon
    pygame.draw.circle(screen,(180,210,255),(900,95),35)
    pygame.draw.circle(screen,(7,9,28),(915,82),32)
    # skyline
    for bx,bw,bh in buildings:
        by=390-bh
        pygame.draw.rect(screen,(18,25,55),(bx,by,bw,bh))
        pygame.draw.rect(screen,(0,210,230),(bx,by,bw,3))
        for wx in range(bx+10,bx+bw-5,18):
            for wy in range(by+15,380,25):
                if random.Random(wx*wy).random()>.3:
                    pygame.draw.rect(screen,random.choice([(0,180,210),(230,50,180),(230,190,70)]),(wx,wy,7,11))
    # road and wet reflection
    pygame.draw.rect(screen,(17,19,30),(0,390,W,290))
    for yy in (470,590):
        pygame.draw.line(screen,(90,95,120),(0,yy),(W,yy),2)
    for i in range(35):
        rx=(i*53+int(t*90))%W
        pygame.draw.line(screen,(30,65,85),(rx,405),(rx+random.randint(15,55),670),1)
    # cars
    for c in cars:
        c[0]+=150*dt
        if c[0]>W+220: c[0]=-180
        pygame.draw.rect(screen,c[2],(int(c[0]),510,105,32),border_radius=8)
        pygame.draw.rect(screen,(15,20,35),(int(c[0])+18,495,58,20),border_radius=5)
        pygame.draw.circle(screen,(5,5,8),(int(c[0])+22,545),10)
        pygame.draw.circle(screen,(5,5,8),(int(c[0])+82,545),10)
        pygame.draw.line(screen,c[2],(int(c[0])+100,525),(int(c[0])+145,525),3)
    # rain
    for r in rain:
        r[1]+=r[2]*dt*22; r[0]-=dt*35
        if r[1]>H: r[1]=-10; r[0]=random.randrange(W)
        pygame.draw.line(screen,(90,145,190),(int(r[0]),int(r[1])),(int(r[0]-4),int(r[1]+12)),1)
    pygame.draw.rect(screen,(5,12,30),(15,15,440,75),border_radius=10)
    screen.blit(font.render("CYBERPUNK DHAKA",True,(0,240,255)),(30,25))
    screen.blit(small.render("NEON LIGHTING | RAIN | TRAFFIC | REFLECTION",True,(255,80,210)),(30,58))
    pygame.display.flip()
pygame.quit(); sys.exit()
