"""
Wumpus World - Modern 2D Pygame Project
Modes: Manual + AI Agent
Controls:
  WASD / Arrow keys : Move
  SPACE             : Shoot in facing direction (one arrow)
  E                 : Grab gold
  M                 : Toggle Manual / AI mode
  F                 : Toggle AI auto-play
  N                 : AI takes one step
  R                 : Restart world
  ESC               : Quit
Install:
  python -m pip install pygame
Run:
  python wumpus_world.py
"""
import random
import sys
from collections import deque

import pygame

# ----------------------------- Configuration -----------------------------
WIDTH, HEIGHT = 1120, 760
FPS = 60
GRID = 6
CELL = 82
BOARD_X, BOARD_Y = 54, 142
BOARD_SIZE = GRID * CELL
PANEL_X = BOARD_X + BOARD_SIZE + 34
PANEL_W = WIDTH - PANEL_X - 34

BG = (13, 20, 34)
PANEL = (24, 35, 54)
PANEL_2 = (31, 46, 68)
TEXT = (235, 242, 250)
MUTED = (151, 169, 191)
TEAL = (45, 212, 191)
GOLD = (255, 196, 76)
RED = (248, 95, 105)
BLUE = (83, 155, 255)
GREEN = (91, 210, 145)
TILE_A = (48, 68, 89)
TILE_B = (39, 57, 77)
TILE_SAFE = (43, 86, 79)
TILE_DANGER = (94, 53, 62)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World | AI Cave Explorer")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("segoeui", 20)
SMALL = pygame.font.SysFont("segoeui", 15)
MED = pygame.font.SysFont("segoeui", 25, bold=True)
BIG = pygame.font.SysFont("segoeui", 34, bold=True)
TITLE = pygame.font.SysFont("segoeui", 39, bold=True)


def draw_text(surface, text, font, color, x, y):
    surface.blit(font.render(str(text), True, color), (x, y))


def cell_center(pos):
    r, c = pos
    return BOARD_X + c * CELL + CELL // 2, BOARD_Y + r * CELL + CELL // 2


def neighbors(pos):
    r, c = pos
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID and 0 <= nc < GRID:
            yield (nr, nc)


class WumpusWorld:
    def __init__(self):
        self.reset()

    def reset(self):
        self.start = (GRID - 1, 0)
        cells = [(r, c) for r in range(GRID) for c in range(GRID)
                 if (r, c) != self.start]
        random.shuffle(cells)
        self.wumpus = cells.pop()
        self.gold = cells.pop()
        self.pits = set(cells[:7])
        self.agent = self.start
        self.facing = (0, 1)
        self.arrow = True
        self.has_gold = False
        self.score = 0
        self.steps = 0
        self.alive = True
        self.won = False
        self.message = "Find the gold, then return to the starting tile!"
        self.visited = {self.start}
        self.percepts_seen = {}
        self.ai_safe = {self.start}
        self.ai_danger = set()
        self.ai_path = []
        self.ai_note = "AI is waiting. Switch to AI mode or press N."
        self.ai_auto = False
        self.mode = "MANUAL"
        self.wumpus_alive = True
        self.reveal = False
        self.last_action = "Game started"

    def adjacent_wumpus(self, pos):
        return self.wumpus_alive and self.wumpus in set(neighbors(pos))

    def percepts(self, pos):
        breeze = any(n in self.pits for n in neighbors(pos))
        stench = self.adjacent_wumpus(pos)
        glitter = pos == self.gold and not self.has_gold
        return breeze, stench, glitter

    def move(self, dr, dc):
        if not self.alive or self.won:
            return
        nr, nc = self.agent[0] + dr, self.agent[1] + dc
        if not (0 <= nr < GRID and 0 <= nc < GRID):
            self.message = "The cave wall blocks your way."
            return
        self.facing = (dr, dc)
        self.agent = (nr, nc)
        self.steps += 1
        self.score -= 1
        self.visited.add(self.agent)
        self.last_action = f"Moved to {self.agent}"
        if self.agent in self.pits:
            self.alive = False
            self.message = "You fell into a pit! Game over."
            self.score -= 100
        elif self.wumpus_alive and self.agent == self.wumpus:
            self.alive = False
            self.message = "The Wumpus caught you! Game over."
            self.score -= 100
        else:
            self.message = self.describe_percepts()

    def describe_percepts(self):
        breeze, stench, glitter = self.percepts(self.agent)
        hints = []
        if breeze:
            hints.append("Breeze: a pit is nearby")
        if stench:
            hints.append("Stench: Wumpus is nearby")
        if glitter:
            hints.append("Glitter: gold is here — press E")
        return " | ".join(hints) if hints else "Quiet cave. No danger detected nearby."

    def grab(self):
        if not self.alive or self.won:
            return
        if self.agent == self.gold and not self.has_gold:
            self.has_gold = True
            self.score += 100
            self.message = "Gold collected! Return to the entrance."
            self.last_action = "Collected gold"
            if self.agent == self.start:
                self.won = True
        else:
            self.message = "There is no gold on this tile."

    def shoot(self):
        if not self.alive or self.won:
            return
        if not self.arrow:
            self.message = "Your only arrow has already been used."
            return
        self.arrow = False
        self.score -= 10
        r, c = self.agent
        dr, dc = self.facing
        for _ in range(GRID):
            r += dr
            c += dc
            if not (0 <= r < GRID and 0 <= c < GRID):
                break
            if self.wumpus_alive and (r, c) == self.wumpus:
                self.wumpus_alive = False
                self.score += 50
                self.message = "Direct hit! The Wumpus is gone. The cave is safer."
                self.last_action = "Wumpus defeated"
                return
        self.message = "The arrow missed. Your arrow is gone."
        self.last_action = "Arrow missed"

    def finish_if_home(self):
        if self.has_gold and self.agent == self.start and self.alive:
            self.won = True
            self.score += 100
            self.message = "You escaped with the gold. Victory!"
            self.last_action = "Escaped with gold"


class CaveAI:
    """A compact knowledge-based explorer using percepts and safe frontier search."""
    def __init__(self, world):
        self.world = world
        self.known_safe = {world.start}
        self.known_visited = set()
        self.known_no_wumpus = set()
        self.known_no_pit = set()
        self.last_pos = None
        self.plan = []

    def reset_knowledge(self):
        self.__init__(self.world)

    def observe(self):
        w = self.world
        pos = w.agent
        breeze, stench, glitter = w.percepts(pos)
        self.known_visited.add(pos)
        self.known_safe.add(pos)
        if not breeze:
            self.known_no_pit.update(neighbors(pos))
        if not stench:
            self.known_no_wumpus.update(neighbors(pos))
        # If the Wumpus has been killed, its location is no longer hazardous.
        if not w.wumpus_alive:
            self.known_no_wumpus.update((r, c) for r in range(GRID) for c in range(GRID))
        for n in neighbors(pos):
            if n in self.known_no_pit and n in self.known_no_wumpus:
                self.known_safe.add(n)
        if pos == w.gold and not w.has_gold:
            w.grab()
        w.ai_danger = {
            n for n in neighbors(pos)
            if n not in self.known_safe
        }
        return breeze, stench, glitter

    def shortest_path(self, start, goals, allowed):
        queue = deque([(start, [])])
        seen = {start}
        while queue:
            pos, path = queue.popleft()
            if pos in goals and pos != start:
                return path
            for nxt in neighbors(pos):
                if nxt in allowed and nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return None

    def next_move(self):
        w = self.world
        if not w.alive or w.won:
            return "Game is over."
        self.observe()

        # Gold secured: navigate back using the known safe route.
        if w.has_gold:
            path = self.shortest_path(w.agent, {w.start}, self.known_safe)
            if path:
                nxt = path[0]
                self._move_to(nxt)
                w.finish_if_home()
                return "Returning to entrance."
            if w.agent == w.start:
                w.finish_if_home()
                return "At entrance."
            return "No known safe route home."

        # Choose a reachable, safe, unvisited frontier.
        frontier = self.known_safe - self.known_visited
        path = self.shortest_path(w.agent, frontier, self.known_safe)
        if path:
            self._move_to(path[0])
            return "Exploring a known safe tile."

        # No guaranteed-safe frontier remains. Make a conservative inference:
        # choose an unvisited neighbor with the fewest unresolved hazards.
        candidates = [n for n in neighbors(w.agent) if n not in self.known_visited]
        if candidates:
            def risk(pos):
                pit_risk = 0 if pos in self.known_no_pit else 1
                wumpus_risk = 0 if pos in self.known_no_wumpus or not w.wumpus_alive else 1
                return (pit_risk + wumpus_risk, pit_risk, wumpus_risk)
            candidates.sort(key=risk)
            choice = candidates[0]
            self._move_to(choice)
            return "Taking the lowest-risk unknown route."
        return "No unvisited route available. Try manual mode."

    def _move_to(self, nxt):
        r, c = self.world.agent
        dr, dc = nxt[0] - r, nxt[1] - c
        self.world.move(dr, dc)
        self.world.ai_note = self.world.last_action


world = WumpusWorld()
ai = CaveAI(world)


def restart():
    global world, ai
    world = WumpusWorld()
    ai = CaveAI(world)


def draw_agent(surface, center):
    x, y = center
    pygame.draw.ellipse(surface, (0, 0, 0), (x-17, y+18, 34, 8))
    pygame.draw.circle(surface, (246, 196, 118), (x, y-10), 12)
    pygame.draw.circle(surface, (36, 48, 66), (x-4, y-12), 2)
    pygame.draw.circle(surface, (36, 48, 66), (x+4, y-12), 2)
    pygame.draw.rect(surface, (64, 168, 225), (x-14, y+2, 28, 25), border_radius=8)
    pygame.draw.line(surface, (245, 220, 180), (x-8, y+25), (x-13, y+34), 4)
    pygame.draw.line(surface, (245, 220, 180), (x+8, y+25), (x+13, y+34), 4)


def draw_pit(surface, center):
    x, y = center
    pygame.draw.ellipse(surface, (16, 22, 34), (x-25, y-18, 50, 36))
    pygame.draw.ellipse(surface, (5, 8, 14), (x-18, y-12, 36, 24))
    pygame.draw.arc(surface, (126, 143, 166), (x-24, y-17, 48, 32), 0.2, 2.8, 3)


def draw_wumpus(surface, center):
    x, y = center
    pygame.draw.ellipse(surface, (0, 0, 0), (x-24, y+20, 48, 8))
    pygame.draw.circle(surface, (184, 67, 83), (x, y), 23)
    pygame.draw.circle(surface, (219, 91, 105), (x-8, y-8), 9)
    pygame.draw.polygon(surface, (240, 225, 210), [(x-17,y-13),(x-22,y-28),(x-7,y-20)])
    pygame.draw.polygon(surface, (240, 225, 210), [(x+17,y-13),(x+22,y-28),(x+7,y-20)])
    pygame.draw.circle(surface, (255, 244, 230), (x-8, y-3), 4)
    pygame.draw.circle(surface, (255, 244, 230), (x+8, y-3), 4)
    pygame.draw.circle(surface, (35, 24, 32), (x-8, y-3), 2)
    pygame.draw.circle(surface, (35, 24, 32), (x+8, y-3), 2)
    pygame.draw.arc(surface, (55, 20, 28), (x-9, y+4, 18, 12), 3.3, 6.1, 2)


def draw_gold(surface, center):
    x, y = center
    pygame.draw.ellipse(surface, (0, 0, 0), (x-19, y+19, 38, 7))
    pygame.draw.circle(surface, (255, 214, 95), (x, y), 18)
    pygame.draw.circle(surface, (255, 239, 166), (x-5, y-6), 6)
    pygame.draw.circle(surface, (209, 143, 34), (x, y), 18, 2)
    draw_text(surface, "$", SMALL, (128, 83, 16), x-5, y-9)


def draw_board():
    for r in range(GRID):
        for c in range(GRID):
            pos = (r, c)
            x, y = BOARD_X + c*CELL, BOARD_Y + r*CELL
            tile = TILE_A if (r+c) % 2 == 0 else TILE_B
            if pos in world.visited:
                tile = TILE_SAFE
            if world.reveal and (pos in world.pits or pos == world.wumpus):
                tile = TILE_DANGER
            rect = pygame.Rect(x, y, CELL, CELL)
            pygame.draw.rect(screen, tile, rect, border_radius=9)
            pygame.draw.rect(screen, (77, 100, 125), rect, 1, border_radius=9)

            # Percepts are shown as small readable chips on explored squares.
            if pos in world.visited:
                breeze, stench, glitter = world.percepts(pos)
                tags = []
                if breeze: tags.append(("B", (80, 160, 255)))
                if stench: tags.append(("S", (247, 117, 124)))
                if glitter: tags.append(("G", GOLD))
                for j, (label, color) in enumerate(tags):
                    pygame.draw.circle(screen, color, (x+13+j*20, y+13), 8)
                    draw_text(screen, label, SMALL, (15, 25, 39), x+9+j*20, y+3)

            if world.reveal:
                if pos in world.pits:
                    draw_pit(screen, cell_center(pos))
                if pos == world.wumpus:
                    draw_wumpus(screen, cell_center(pos))
                if pos == world.gold and not world.has_gold:
                    draw_gold(screen, cell_center(pos))
            else:
                if pos == world.gold and world.has_gold is False and pos in world.visited:
                    draw_gold(screen, cell_center(pos))
                # Show Wumpus/pits only after discovered or when the world is revealed.
                if pos == world.wumpus and pos in world.visited and world.wumpus_alive:
                    draw_wumpus(screen, cell_center(pos))
                if pos in world.pits and pos in world.visited:
                    draw_pit(screen, cell_center(pos))

    # Start marker.
    sx, sy = cell_center(world.start)
    pygame.draw.circle(screen, (83, 215, 164), (sx, sy+25), 5)
    if world.agent:
        draw_agent(screen, cell_center(world.agent))
    # Direction arrow.
    ax, ay = cell_center(world.agent)
    dx, dy = world.facing[1]*19, world.facing[0]*19
    pygame.draw.line(screen, (255, 255, 255), (ax, ay-25), (ax+dx, ay-25+dy), 3)
    pygame.draw.circle(screen, (255, 255, 255), (ax+dx, ay-25+dy), 4)


def panel_card(rect, title):
    pygame.draw.rect(screen, PANEL, rect, border_radius=16)
    draw_text(screen, title, MED, TEXT, rect.x+17, rect.y+13)


def draw_panel():
    x = PANEL_X
    # Status card.
    panel_card(pygame.Rect(x, 142, PANEL_W, 112), "MISSION STATUS")
    draw_text(screen, f"Mode: {world.mode}", FONT, TEAL, x+18, 190)
    draw_text(screen, f"Score: {world.score}     Steps: {world.steps}", SMALL, MUTED, x+18, 221)

    # Inventory.
    panel_card(pygame.Rect(x, 268, PANEL_W, 104), "INVENTORY")
    draw_text(screen, "Gold: " + ("Collected" if world.has_gold else "Not found"),
              FONT, GOLD if world.has_gold else MUTED, x+18, 315)
    draw_text(screen, "Arrow: " + ("Available" if world.arrow else "Used"),
              SMALL, GREEN if world.arrow else RED, x+18, 345)

    # Percepts.
    panel_card(pygame.Rect(x, 386, PANEL_W, 116), "CURRENT SENSORS")
    breeze, stench, glitter = world.percepts(world.agent)
    sensor_rows = [
        ("Breeze", breeze, BLUE),
        ("Stench", stench, RED),
        ("Glitter", glitter, GOLD),
    ]
    for i, (label, active, color) in enumerate(sensor_rows):
        yy = 430 + i*22
        pygame.draw.circle(screen, color if active else (74, 91, 111), (x+25, yy+8), 6)
        draw_text(screen, f"{label}: {'DETECTED' if active else 'None'}",
                  SMALL, color if active else MUTED, x+40, yy)

    # AI brain.
    panel_card(pygame.Rect(x, 516, PANEL_W, 116), "AI EXPLORER")
    draw_text(screen, f"Known safe tiles: {len(ai.known_safe)}", SMALL, GREEN, x+18, 558)
    draw_text(screen, f"Visited tiles: {len(ai.known_visited)}", SMALL, MUTED, x+18, 581)
    draw_text(screen, "Auto: ON" if world.ai_auto else "Auto: OFF",
              SMALL, TEAL if world.ai_auto else MUTED, x+18, 604)

    # Message / controls.
    panel_card(pygame.Rect(x, 646, PANEL_W, 91), "FIELD REPORT")
    msg = world.message
    if len(msg) > 43:
        msg = msg[:40] + "..."
    draw_text(screen, msg, SMALL, TEXT, x+16, 687)
    draw_text(screen, "WASD move | E grab | SPACE shoot", SMALL, MUTED, x+16, 711)


def draw_header():
    draw_text(screen, "WUMPUS", TITLE, TEXT, 54, 35)
    draw_text(screen, "WORLD", TITLE, TEAL, 235, 35)
    draw_text(screen, "AI CAVE EXPLORER", SMALL, MUTED, 57, 82)
    # Legend.
    legend_y = 105
    items = [("Agent", BLUE), ("Wumpus", RED), ("Gold", GOLD), ("Pit", (120, 139, 160))]
    lx = 420
    for label, color in items:
        pygame.draw.circle(screen, color, (lx, legend_y+9), 6)
        draw_text(screen, label, SMALL, MUTED, lx+12, legend_y)
        lx += 105


def draw_footer():
    draw_text(screen, "M  Mode     F  Auto AI     N  AI step     R  Restart     TAB  Reveal map",
              SMALL, MUTED, 54, 720)


def draw_end_overlay():
    if not (world.won or not world.alive):
        return
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((5, 9, 17, 185))
    screen.blit(shade, (0, 0))
    title = "MISSION COMPLETE!" if world.won else "MISSION FAILED"
    color = GREEN if world.won else RED
    label = BIG.render(title, True, color)
    screen.blit(label, label.get_rect(center=(WIDTH//2, HEIGHT//2-28)))
    sub = FONT.render(f"Final score: {world.score}  |  Press R to play again", True, TEXT)
    screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2+18)))


def toggle_mode():
    world.mode = "AI" if world.mode == "MANUAL" else "MANUAL"
    world.ai_auto = False
    world.message = "AI mode enabled." if world.mode == "AI" else "Manual control enabled."


def handle_key(key):
    if key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    if key == pygame.K_r:
        restart()
        return
    if key == pygame.K_m:
        toggle_mode()
        return
    if key == pygame.K_TAB:
        world.reveal = not world.reveal
        return
    if key == pygame.K_f:
        world.mode = "AI"
        world.ai_auto = not world.ai_auto
        world.message = "AI auto-play started." if world.ai_auto else "AI auto-play paused."
        return
    if key == pygame.K_n:
        world.mode = "AI"
        world.ai_auto = False
        world.ai_note = ai.next_move()
        return
    if world.mode != "MANUAL" or not world.alive or world.won:
        return
    moves = {
        pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
        pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0),
        pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
        pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1),
    }
    if key in moves:
        world.move(*moves[key])
        world.finish_if_home()
    elif key == pygame.K_SPACE:
        world.shoot()
    elif key == pygame.K_e:
        world.grab()
        world.finish_if_home()


def main():
    ai_timer = 0
    running = True
    while running:
        dt = clock.tick(FPS)
        ai_timer += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_key(event.key)

        if world.mode == "AI" and world.ai_auto and ai_timer >= 650:
            ai_timer = 0
            world.ai_note = ai.next_move()
            world.finish_if_home()

        screen.fill(BG)
        draw_header()
        draw_board()
        draw_panel()
        draw_footer()
        draw_end_overlay()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
