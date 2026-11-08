import pygame, random, math, sys
pygame.init()
W,H=1100,680
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption("Deep Ocean Exploration - Computer Graphics Project")
clock=pygame.time.Clock()
font=pygame.font.SysFont("consolas",20,bold=True)
small=pygame.font.SysFont("consolas",15)
bubbles=[[random.randrange(W),random.randrange(H),random.uniform(15,55)] for _ in range(100)]
fish=[[random.randrange(W),random.randrange(130,570),random.choice([-1,1]),random.uniform(35,90)] for _ in range(12)]
coral=[]
for x in range(25,W,70):
    coral.append((x,random.randint(590,640),random.randint(25,75),random.choice([(230,80,110),(230,120,65),(170,80,190)])))
sub_x=350; t=0; running=True
while running:
    dt=clock.tick(60)/1000; t+=dt
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: sub_x-=220*dt
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: sub_x+=220*dt
    sub_x=max(100,min(W-130,sub_x))
    screen.fill((0,28,65))
    # layered water gradient
    for y in range(H):
        col=(0,int(35+y*.055),int(75+y*.09))
        pygame.draw.line(screen,col,(0,y),(W,y))
    # light shafts
    light=pygame.Surface((W,H),pygame.SRCALPHA)
    for i in range(5):
        xx=120+i*210+math.sin(t*.4+i)*25
        pygame.draw.polygon(light,(90,190,220,18),[(xx,0),(xx+65,0),(xx+260,590),(xx+160,590)])
    screen.blit(light,(0,0))
    # seabed
    pygame.draw.rect(screen,(15,65,60),(0,610,W,70))
    for x,y,h,c in coral:
        pygame.draw.line(screen,c,(x,y),(x-12,y-h),7)
        pygame.draw.line(screen,c,(x,y-15),(x+17,y-h*.75),6)
        pygame.draw.circle(screen,c,(x-12,y-h),7)
        pygame.draw.circle(screen,c,(x+17,y-int(h*.75)),6)
    # fish
    for f in fish:
        f[0]+=f[2]*f[3]*dt
        if f[0]<-40: f[0]=W+30
        if f[0]>W+40: f[0]=-30
        x,y,d,_=f; color=(70,190,220) if int(y)%2 else (245,165,65)
        pygame.draw.ellipse(screen,color,(int(x),int(y),35,17))
        tailx=x+(0 if d>0 else 35)
        pygame.draw.polygon(screen,color,[(tailx,y+8),(tailx+( -13 if d>0 else 13),y),(tailx+(-13 if d>0 else 13),y+16)])
        pygame.draw.circle(screen,(5,20,35),(int(x+25 if d>0 else x+9),int(y+6)),2)
    # submarine body
    sy=310+math.sin(t*1.8)*12
    pygame.draw.ellipse(screen,(195,145,45),(sub_x,sy,190,75))
    pygame.draw.ellipse(screen,(245,190,75),(sub_x+15,sy+8,155,55),3)
    pygame.draw.rect(screen,(175,125,35),(sub_x+75,sy-27,48,30),border_radius=8)
    pygame.draw.ellipse(screen,(80,210,230),(sub_x+82,sy-21,34,18))
    pygame.draw.circle(screen,(80,230,255),(sub_x+180,sy+37),9)
    # bubbles
    for b in bubbles:
        b[1]-=b[2]*dt
        if b[1]<-10: b[1]=H+10; b[0]=random.randrange(W)
        pygame.draw.circle(screen,(150,225,245),(int(b[0]),int(b[1])),2,1)
    # hud
    pygame.draw.rect(screen,(2,18,45),(15,15,455,80),border_radius=10)
    screen.blit(font.render("DEEP OCEAN EXPLORER",True,(110,230,255)),(30,25))
    screen.blit(small.render("A / D or LEFT / RIGHT : MOVE SUBMARINE",True,(220,240,255)),(30,60))
    pygame.display.flip()
pygame.quit(); sys.exit()
