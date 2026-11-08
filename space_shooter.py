"""
GALAXY ASSAULT - 2D Space Shooter
Python + Pygame. No external image or sound assets required.

Install:
    python -m pip install pygame
Run:
    python space_shooter.py

Controls:
    A / Left Arrow  : Move left
    D / Right Arrow : Move right
    W / Up Arrow    : Move up
    S / Down Arrow  : Move down
    Shooting        : Automatic
    P               : Pause / resume
    R               : Restart after game over
    ESC             : Quit
"""
import math
import random
import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 700
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GALAXY ASSAULT | Space Shooter")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("segoeui", 20)
SMALL = pygame.font.SysFont("segoeui", 15)
MED = pygame.font.SysFont("segoeui", 28, bold=True)
BIG = pygame.font.SysFont("segoeui", 48, bold=True)

BG = (7, 12, 29)
WHITE = (238, 246, 255)
CYAN = (67, 225, 245)
BLUE = (69, 133, 255)
PINK = (255, 91, 156)
GOLD = (255, 202, 83)
GREEN = (89, 235, 164)
MUTED = (137, 160, 191)

def clamp(value, low, high):
    return max(low, min(high, value))

def text(surface, value, font, color, x, y, center=False):
    img = font.render(str(value), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)

def glow_circle(surface, color, center, radius, strength=90):
    layer = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*color, strength), (radius*2, radius*2), radius*2)
    pygame.draw.circle(layer, (*color, min(255, strength+80)), (radius*2, radius*2), radius)
    surface.blit(layer, (center[0]-radius*2, center[1]-radius*2), special_flags=pygame.BLEND_ADD)

class Star:
    def __init__(self):
        self.reset(random.randint(0, HEIGHT))
    def reset(self, y=-10):
        self.x = random.randrange(WIDTH)
        self.y = y
        self.speed = random.uniform(35, 170)
        self.size = random.choice((1, 1, 1, 2, 2, 3))
        self.color = random.choice(((115, 160, 220), (150, 190, 235), (90, 220, 240)))
    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT + 5:
            self.reset(-5)
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

class Bullet:
    def __init__(self, x, y, vy=-620, friendly=True):
        self.x, self.y = float(x), float(y)
        self.vy = vy
        self.friendly = friendly
        self.radius = 5 if friendly else 6
        self.alive = True
    def update(self, dt):
        self.y += self.vy * dt
        if self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False
    def draw(self, surf):
        color = CYAN if self.friendly else PINK
        glow_circle(surf, color, (int(self.x), int(self.y)), 7, 55)
        pygame.draw.line(surf, color, (int(self.x), int(self.y-10)), (int(self.x), int(self.y+8)), 4)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        angle = random.random() * math.tau
        speed = random.uniform(50, 250)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = self.max_life = random.uniform(.25, .7)
        self.radius = random.randint(2, 5)
        self.color = color
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= .985
        self.vy *= .985
        self.life -= dt
    def draw(self, surf):
        if self.life > 0:
            r = max(1, int(self.radius * self.life / self.max_life))
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)

class PowerUp:
    TYPES = ("rapid", "shield", "heal")
    def __init__(self, x, y, kind=None):
        self.x, self.y = float(x), float(y)
        self.kind = kind or random.choice(self.TYPES)
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.center = (int(x), int(y))
        self.phase = random.random() * 6
    def update(self, dt):
        self.y += 115 * dt
        self.phase += dt * 4
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surf):
        colors = {"rapid": GOLD, "shield": BLUE, "heal": GREEN}
        labels = {"rapid": "RAPID", "shield": "SHIELD", "heal": "HEAL"}
        color = colors[self.kind]
        x, y = self.rect.center
        glow_circle(surf, color, (x, y), 20, 55)
        pygame.draw.circle(surf, color, (x, y), 17, 3)
        pygame.draw.circle(surf, (15, 25, 48), (x, y), 13)

        if self.kind == "rapid":
            bolt = [(x+2, y-11), (x-7, y+1), (x-1, y+1),
                    (x-3, y+11), (x+8, y-3), (x+2, y-3)]
            pygame.draw.polygon(surf, GOLD, bolt)
        elif self.kind == "shield":
            shield = [(x, y-11), (x+9, y-7), (x+7, y+4),
                      (x, y+11), (x-7, y+4), (x-9, y-7)]
            pygame.draw.polygon(surf, (150, 205, 255), shield, 3)
            pygame.draw.line(surf, WHITE, (x, y-6), (x, y+6), 2)
        else:
            pygame.draw.line(surf, GREEN, (x-8, y), (x+8, y), 4)
            pygame.draw.line(surf, GREEN, (x, y-8), (x, y+8), 4)

        text(surf, labels[self.kind], SMALL, color, x, y+25, center=True)

class Enemy:
    def __init__(self, level):
        self.kind = random.choices(("scout", "fighter", "tank"), (55, 35, 10))[0]
        self.x = random.randint(55, WIDTH-55)
        self.y = random.randint(-130, -45)
        self.phase = random.random() * 6
        self.speed = random.uniform(90, 145) + level * 9
        self.hp = {"scout": 1, "fighter": 2, "tank": 4}[self.kind]
        self.max_hp = self.hp
        self.radius = {"scout": 17, "fighter": 22, "tank": 28}[self.kind]
        self.shoot_timer = random.uniform(1.5, 3.0)
        self.alive = True
    def update(self, dt, level, enemy_bullets):
        self.phase += dt * 2
        self.y += self.speed * dt
        self.x += math.sin(self.phase) * 55 * dt
        self.x = clamp(self.x, self.radius+5, WIDTH-self.radius-5)
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and self.y > 20:
            enemy_bullets.append(Bullet(self.x, self.y+self.radius, vy=300+level*15, friendly=False))
            self.shoot_timer = random.uniform(2.2, 3.6)
        if self.y > HEIGHT + 40:
            self.alive = False
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if self.kind == "scout":
            points = [(x, y+20), (x-18, y-14), (x, y-6), (x+18, y-14)]
            pygame.draw.polygon(surf, (235, 92, 120), points)
            pygame.draw.polygon(surf, (255, 175, 190), points, 2)
            pygame.draw.circle(surf, GOLD, (x, y+3), 4)
        elif self.kind == "fighter":
            points = [(x, y+23), (x-24, y-10), (x-8, y-6), (x, y-20),
                      (x+8, y-6), (x+24, y-10)]
            pygame.draw.polygon(surf, (151, 95, 238), points)
            pygame.draw.polygon(surf, (210, 183, 255), points, 2)
            pygame.draw.circle(surf, CYAN, (x, y+2), 5)
        else:
            pygame.draw.rect(surf, (181, 77, 82), (x-25, y-21, 50, 42), border_radius=9)
            pygame.draw.rect(surf, (255, 160, 135), (x-25, y-21, 50, 42), 2, border_radius=9)
            pygame.draw.circle(surf, GOLD, (x, y), 8)
        if self.max_hp > 1:
            pygame.draw.rect(surf, (45, 50, 70), (x-20, y-self.radius-9, 40, 4), border_radius=2)
            pygame.draw.rect(surf, GREEN, (x-20, y-self.radius-9, int(40*self.hp/self.max_hp), 4), border_radius=2)

class Player:
    def __init__(self):
        self.x, self.y = WIDTH/2, HEIGHT-90
        self.speed = 360
        self.rect = pygame.Rect(0, 0, 42, 48)
        self.rect.center = (int(self.x), int(self.y))
        self.lives = 5
        self.shield = 0
        self.rapid = 0
        self.invulnerable = 0
        self.cooldown = 0
    def update(self, dt, keys):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        length = math.hypot(dx, dy)
        if length:
            dx, dy = dx/length, dy/length
        self.x = clamp(self.x + dx*self.speed*dt, 28, WIDTH-28)
        self.y = clamp(self.y + dy*self.speed*dt, 65, HEIGHT-35)
        self.rect.center = (int(self.x), int(self.y))
        self.cooldown = max(0, self.cooldown-dt)
        self.shield = max(0, self.shield-dt)
        self.rapid = max(0, self.rapid-dt)
        self.invulnerable = max(0, self.invulnerable-dt)
    def fire(self, bullets):
        if self.cooldown > 0:
            return
        bullets.append(Bullet(self.x-12, self.y-22))
        bullets.append(Bullet(self.x+12, self.y-22))
        if self.rapid > 0:
            bullets.append(Bullet(self.x, self.y-30, vy=-760))
            self.cooldown = .12
        else:
            self.cooldown = .28
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if self.invulnerable > 0 and int(self.invulnerable*12) % 2 == 0:
            return
        glow_circle(surf, CYAN, (x, y), 24, 45)
        flame_h = random.randint(12, 23)
        pygame.draw.polygon(surf, GOLD, [(x-7,y+19),(x,y+19+flame_h),(x+7,y+19)])
        pygame.draw.polygon(surf, (255, 245, 190), [(x-3,y+19),(x,y+19+flame_h//2),(x+3,y+19)])
        points = [(x, y-29), (x-12, y+13), (x-30, y+25), (x-28, y+31),
                  (x-7, y+25), (x, y+31), (x+7, y+25), (x+28, y+31),
                  (x+30, y+25), (x+12, y+13)]
        pygame.draw.polygon(surf, (60, 178, 220), points)
        pygame.draw.polygon(surf, (210, 250, 255), points, 2)
        pygame.draw.polygon(surf, (225, 250, 255), [(x,y-21),(x-6,y+10),(x+6,y+10)])
        pygame.draw.ellipse(surf, (20, 55, 91), (x-6, y-5, 12, 17))
        pygame.draw.ellipse(surf, CYAN, (x-4, y-3, 8, 10))
        pygame.draw.line(surf, (245, 255, 255), (x-2, y-17), (x+2, y-7), 2)
        pygame.draw.circle(surf, (255, 255, 255), (x-19, y+25), 2)
        pygame.draw.circle(surf, (255, 255, 255), (x+19, y+25), 2)
        if self.shield > 0:
            pygame.draw.circle(surf, (100, 180, 255), (x, y), 39, 3)
            pygame.draw.circle(surf, (100, 180, 255), (x, y), 43, 1)

class Game:
    def __init__(self):
        self.stars = [Star() for _ in range(115)]
        self.reset()
    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.powerups = []
        self.score = 0
        self.level = 1
        self.spawn_timer = .7
        self.power_timer = 10
        self.paused = False
        self.game_over = False
        self.elapsed = 0
    def explode(self, x, y, color, amount=18):
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))
    def damage_player(self):
        p = self.player
        if p.invulnerable > 0:
            return
        if p.shield > 0:
            p.shield = 0
            p.invulnerable = 1.0
            self.explode(p.x, p.y, BLUE, 22)
            return
        p.lives -= 1
        p.invulnerable = 1.5
        self.explode(p.x, p.y, PINK, 25)
        if p.lives <= 0:
            self.game_over = True
    def update(self, dt):
        for star in self.stars:
            star.update(dt)
        if self.paused or self.game_over:
            return
        self.elapsed += dt
        self.level = 1 + self.score // 250
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.player.fire(self.bullets)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.enemies.append(Enemy(self.level))
            self.spawn_timer = max(.32, 1.15 - self.level*.055)
        self.power_timer -= dt
        if self.power_timer <= 0:
            if random.random() < .82:
                self.powerups.append(PowerUp(random.randint(40, WIDTH-40), -20))
            self.power_timer = random.uniform(11, 16)

        for obj in self.bullets + self.enemy_bullets:
            obj.update(dt)
        for enemy in self.enemies:
            enemy.update(dt, self.level, self.enemy_bullets)
        for power in self.powerups:
            power.update(dt)
        for particle in self.particles:
            particle.update(dt)

        for bullet in self.bullets:
            if not bullet.alive:
                continue
            for enemy in self.enemies:
                if enemy.alive and math.hypot(bullet.x-enemy.x, bullet.y-enemy.y) < enemy.radius+bullet.radius:
                    bullet.alive = False
                    enemy.hp -= 1
                    self.explode(bullet.x, bullet.y, CYAN, 4)
                    if enemy.hp <= 0:
                        enemy.alive = False
                        self.score += {"scout": 20, "fighter": 35, "tank": 60}[enemy.kind]
                        self.explode(enemy.x, enemy.y, PINK if enemy.kind != "tank" else GOLD, 24)
                        if random.random() < .12:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))
                    break

        for bullet in self.enemy_bullets:
            if bullet.alive and self.player.rect.inflate(-8, -8).collidepoint(bullet.x, bullet.y):
                bullet.alive = False
                self.damage_player()
        for enemy in self.enemies:
            if enemy.alive and self.player.rect.inflate(-8, -8).colliderect(
                    pygame.Rect(enemy.x-enemy.radius, enemy.y-enemy.radius,
                                enemy.radius*2, enemy.radius*2)):
                enemy.alive = False
                self.explode(enemy.x, enemy.y, PINK, 18)
                self.damage_player()

        for power in self.powerups:
            if self.player.rect.colliderect(power.rect):
                if power.kind == "rapid":
                    self.player.rapid = 8
                elif power.kind == "shield":
                    self.player.shield = 8
                else:
                    self.player.lives = min(5, self.player.lives+1)
                self.explode(power.x, power.y, GREEN, 12)
                power.y = HEIGHT + 100

        self.bullets = [b for b in self.bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        self.powerups = [p for p in self.powerups if p.y < HEIGHT+40]
        self.particles = [p for p in self.particles if p.life > 0]

    def draw_background(self):
        for y in range(0, HEIGHT, 4):
            t = y / HEIGHT
            col = (int(5 + 8*t), int(10 + 13*t), int(27 + 24*t))
            pygame.draw.rect(screen, col, (0, y, WIDTH, 4))

        for i in range(4):
            x = (i*307 + int(self.elapsed*(5+i))) % (WIDTH+260) - 130
            y = 190 + (i % 3)*165
            glow_circle(screen, ((23, 48, 105) if i % 2 == 0 else (18, 72, 88)),
                        (x, y), 76, 7)

        px = int(835 + math.sin(self.elapsed*0.12)*10)
        py = 185
        glow_circle(screen, (55, 72, 125), (px, py), 43, 7)
        pygame.draw.ellipse(screen, (48, 63, 105), (px-34, py-26, 68, 52))
        pygame.draw.ellipse(screen, (91, 111, 158), (px-34, py-26, 68, 52), 1)
        pygame.draw.arc(screen, (112, 104, 153), (px-55, py-12, 110, 35),
                        math.radians(195), math.radians(345), 2)
        pygame.draw.arc(screen, (73, 91, 139), (px-55, py-12, 110, 35),
                        math.radians(15), math.radians(165), 2)

        for star in self.stars:
            star.draw(screen)

    def draw_hud(self):
        pygame.draw.rect(screen, (10, 19, 39), (0, 0, WIDTH, 61))
        pygame.draw.line(screen, (38, 78, 112), (0, 60), (WIDTH, 60), 2)

        title_font = pygame.font.SysFont("segoeui", 31, bold=True)
        title_surface = title_font.render("GALAXY ASSAULT", True, WHITE)
        title_rect = title_surface.get_rect(center=(205, 30))
        screen.blit(title_surface, title_rect)
        pygame.draw.line(screen, CYAN, (title_rect.left, 53),
                         (title_rect.right, 53), 2)

        cards = [
            (405, 12, 150, f"SCORE  {self.score:06d}", GOLD),
            (568, 12, 112, f"LEVEL  {self.level}", WHITE),
            (693, 12, 142, f"LIVES  {self.player.lives}/5", PINK),
        ]
        for x, y, w, label, color in cards:
            pygame.draw.rect(screen, (23, 39, 64), (x, y, w, 37), border_radius=10)
            pygame.draw.rect(screen, (53, 79, 112), (x, y, w, 37), 1, border_radius=10)
            text(screen, label, SMALL, color, x+12, y+10)

        for i in range(5):
            hx, hy = 858 + i*25, 30
            heart_color = PINK if i < self.player.lives else (75, 86, 110)
            pygame.draw.circle(screen, heart_color, (hx-4, hy-3), 5)
            pygame.draw.circle(screen, heart_color, (hx+4, hy-3), 5)
            pygame.draw.polygon(screen, heart_color,
                                [(hx-9, hy-1), (hx+9, hy-1), (hx, hy+10)])
            if i >= self.player.lives:
                pygame.draw.circle(screen, (130, 143, 165), (hx-4, hy-3), 5, 1)
                pygame.draw.circle(screen, (130, 143, 165), (hx+4, hy-3), 5, 1)
                pygame.draw.polygon(screen, (130, 143, 165),
                                    [(hx-9, hy-1), (hx+9, hy-1), (hx, hy+10)], 1)

        if self.player.rapid > 0:
            pygame.draw.rect(screen, (72, 55, 27), (26, 72, 150, 42), border_radius=9)
            text(screen, f"RAPID FIRE  {self.player.rapid:0.1f}s", SMALL, GOLD, 35, 77)
            pygame.draw.rect(screen, (35, 32, 25), (35, 99, 132, 5), border_radius=3)
            pygame.draw.rect(screen, GOLD, (35, 99, int(132*self.player.rapid/8), 5), border_radius=3)
        if self.player.shield > 0:
            pygame.draw.rect(screen, (25, 48, 87), (185, 72, 155, 42), border_radius=9)
            text(screen, f"SHIELD  {self.player.shield:0.1f}s", SMALL, (143, 193, 255), 194, 77)
            pygame.draw.rect(screen, (24, 35, 55), (194, 99, 136, 5), border_radius=3)
            pygame.draw.rect(screen, (110, 180, 255), (194, 99, int(136*self.player.shield/8), 5), border_radius=3)

        pygame.draw.rect(screen, (9, 17, 34), (0, HEIGHT-48, WIDTH, 48))
        pygame.draw.line(screen, (36, 76, 112), (0, HEIGHT-48), (WIDTH, HEIGHT-48), 1)
        text(screen, "PILOT CONTROLS", SMALL, CYAN, 24, HEIGHT-32)
        text(screen, "WASD / ARROWS  MOVE", SMALL, MUTED, 175, HEIGHT-32)
        text(screen, "AUTO LASERS  ACTIVE", SMALL, GREEN, 390, HEIGHT-32)
        text(screen, "P  PAUSE", SMALL, MUTED, 610, HEIGHT-32)
        text(screen, "R  RESTART AFTER DEFEAT", SMALL, MUTED, 730, HEIGHT-32)

    def draw(self):
        self.draw_background()
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw(screen)
        for power in self.powerups:
            power.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
        self.player.draw(screen)
        self.draw_hud()
        if self.paused:
            self.overlay("PAUSED", "Press P to continue")
        if self.game_over:
            self.overlay("SHIP DESTROYED", "Press R to launch again", gameover=True)
        pygame.display.flip()

    def overlay(self, title, subtitle, gameover=False):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((3, 7, 18, 190))
        screen.blit(veil, (0, 0))
        color = PINK if gameover else CYAN
        text(screen, title, BIG, color, WIDTH//2, HEIGHT//2-35, center=True)
        text(screen, subtitle, FONT, WHITE, WIDTH//2, HEIGHT//2+20, center=True)
        if gameover:
            text(screen, f"FINAL SCORE: {self.score}", MED, GOLD,
                 WIDTH//2, HEIGHT//2+62, center=True)

def main():
    game = Game()
    running = True
    while running:
        dt = min(clock.tick(FPS)/1000.0, .035)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p and not game.game_over:
                    game.paused = not game.paused
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()
        game.update(dt)
        game.draw()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
