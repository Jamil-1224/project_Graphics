import pygame
import chess
import sys


pygame.init()
WIDTH, HEIGHT = 1000, 760
BOARD_SIZE = 640
SQ = BOARD_SIZE // 8
BOARD_X, BOARD_Y = 30, 60
PANEL_X = 710

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Chess Board Game")
clock = pygame.time.Clock()

TITLE = pygame.font.SysFont("arial", 30, bold=True)
FONT = pygame.font.SysFont("arial", 20)
SMALL = pygame.font.SysFont("arial", 15)

LIGHT = (232, 237, 243)       # cool ivory
DARK = (91, 112, 139)         # slate blue
SELECT = (28, 190, 190)       # bright teal
LAST = (246, 190, 75)         # warm amber
MOVE_DOT = (22, 163, 130)     # teal move markers
BG = (30, 38, 48)
PANEL = (43, 53, 66)
WHITE_PIECE = (250, 248, 239)
BLACK_PIECE = (38, 45, 58)

board = chess.Board()
selected_square = None
legal_targets = []
move_history = []
scroll_offset = 0
message = "White to move"
running = True


def draw_text(surface, text, font, color, x, y):
    image = font.render(text, True, color)
    surface.blit(image, (x, y))



def draw_piece(surface, piece, center, square_size):
    """Draw a recognizable chess piece with Pygame vector primitives.
    This avoids missing Unicode chess fonts on Windows.
    """
    cx, cy = center
    s = square_size / 100.0
    white = piece.color == chess.WHITE

    if white:
        fill = (250, 248, 239)
        edge = (70, 78, 91)
        shade = (205, 211, 218)
        accent = (190, 145, 65)
    else:
        fill = (39, 47, 61)
        edge = (12, 17, 26)
        shade = (83, 96, 114)
        accent = (221, 184, 104)

    def pt(x, y):
        return (int(cx + x*s), int(cy + y*s))

    def polygon(points, color, outline=edge, width=2):
        pts = [pt(x, y) for x, y in points]
        pygame.draw.polygon(surface, color, pts)
        if outline:
            pygame.draw.polygon(surface, outline, pts, max(1, int(width*s)))

    def ellipse(x, y, w, h, color, outline=edge, width=2):
        rect = pygame.Rect(int(cx+(x-w/2)*s), int(cy+(y-h/2)*s),
                           max(1, int(w*s)), max(1, int(h*s)))
        pygame.draw.ellipse(surface, color, rect)
        if outline:
            pygame.draw.ellipse(surface, outline, rect, max(1, int(width*s)))

    def line(points, color, width=3):
        pygame.draw.lines(surface, color, False, [pt(x, y) for x, y in points],
                          max(1, int(width*s)))

    # Soft drop shadow gives every piece separation from the square.
    shadow = pygame.Rect(int(cx-29*s), int(cy+29*s), int(58*s), max(2, int(8*s)))
    pygame.draw.ellipse(surface, (0, 0, 0, 65), shadow)

    kind = piece.piece_type

    # Shared pedestal.
    ellipse(0, 31, 58, 12, shade, edge, 2)
    pygame.draw.rect(surface, fill,
                     (int(cx-25*s), int(cy+18*s), int(50*s), int(10*s)),
                     border_radius=max(2, int(4*s)))
    pygame.draw.rect(surface, edge,
                     (int(cx-25*s), int(cy+18*s), int(50*s), int(10*s)),
                     max(1, int(2*s)), border_radius=max(2, int(4*s)))
    ellipse(0, 18, 50, 10, fill, edge, 2)

    if kind == chess.PAWN:
        polygon([(-13, 17), (-10, -2), (10, -2), (13, 17)], fill)
        ellipse(0, -15, 27, 27, fill, edge, 2)
        ellipse(-5, -20, 6, 6, (255, 255, 255) if white else shade, None)
    elif kind == chess.ROOK:
        pygame.draw.rect(surface, fill,
                         (int(cx-19*s), int(cy-27*s), int(38*s), int(47*s)))
        pygame.draw.rect(surface, edge,
                         (int(cx-19*s), int(cy-27*s), int(38*s), int(47*s)),
                         max(1, int(2*s)))
        pygame.draw.rect(surface, shade,
                         (int(cx-15*s), int(cy-23*s), int(8*s), int(37*s)))
        for x in (-16, -5, 6):
            pygame.draw.rect(surface, fill,
                             (int(cx+x*s), int(cy-38*s), int(10*s), int(14*s)))
            pygame.draw.rect(surface, edge,
                             (int(cx+x*s), int(cy-38*s), int(10*s), int(14*s)),
                             max(1, int(2*s)))
        line([(-19, -25), (19, -25)], accent, 2)
    elif kind == chess.KNIGHT:
        polygon([(-20, 18), (-18, 2), (-10, -8), (-18, -20),
                 (-8, -37), (8, -32), (21, -15), (14, -4),
                 (19, 18)], fill)
        polygon([(-8, -31), (-3, -43), (8, -33), (2, -23)], shade)
        ellipse(6, -25, 5, 5, accent, edge, 1)
        line([(-8, -8), (9, -5), (15, 2)], shade, 3)
    elif kind == chess.BISHOP:
        polygon([(-15, 17), (-11, -5), (-7, -16), (-13, -27),
                 (0, -43), (13, -27), (7, -16), (11, -5),
                 (15, 17)], fill)
        ellipse(0, -39, 11, 11, accent, edge, 1)
        line([(-5, -29), (5, -20)], edge, 3)
        ellipse(0, -7, 31, 8, shade, edge, 1)
    elif kind == chess.QUEEN:
        polygon([(-20, 17), (-15, -8), (-22, -29), (-8, -18),
                 (0, -39), (8, -18), (22, -29), (15, -8),
                 (20, 17)], fill)
        for x, y in [(-22, -29), (-8, -18), (0, -40), (8, -18), (22, -29)]:
            ellipse(x, y, 9, 9, accent, edge, 1)
        line([(-15, -8), (15, -8)], accent, 2)
    elif kind == chess.KING:
        polygon([(-18, 17), (-13, -9), (-9, -24), (9, -24),
                 (13, -9), (18, 17)], fill)
        pygame.draw.rect(surface, fill,
                         (int(cx-3*s), int(cy-47*s), int(6*s), int(29*s)))
        pygame.draw.rect(surface, edge,
                         (int(cx-3*s), int(cy-47*s), int(6*s), int(29*s)),
                         max(1, int(1.5*s)))
        pygame.draw.rect(surface, fill,
                         (int(cx-13*s), int(cy-39*s), int(26*s), int(6*s)))
        pygame.draw.rect(surface, edge,
                         (int(cx-13*s), int(cy-39*s), int(26*s), int(6*s)),
                         max(1, int(1.5*s)))
        line([(-10, -7), (10, -7)], accent, 2)


def draw_square_overlay(square, color, alpha=90):
    overlay = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    screen.blit(overlay, square_rect(square).topleft)


def square_rect(square):
    file_no = chess.square_file(square)
    rank_no = chess.square_rank(square)
    x = BOARD_X + file_no * SQ
    y = BOARD_Y + (7 - rank_no) * SQ
    return pygame.Rect(x, y, SQ, SQ)


def current_status():
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return f"CHECKMATE — {winner} wins!"
    if board.is_stalemate():
        return "DRAW — Stalemate"
    if board.is_insufficient_material():
        return "DRAW — Insufficient material"
    if board.is_seventyfive_moves():
        return "DRAW — 75-move rule"
    if board.is_fivefold_repetition():
        return "DRAW — Fivefold repetition"
    if board.is_check():
        return ("White" if board.turn else "Black") + " is in CHECK"
    return ("White" if board.turn else "Black") + " to move"


def draw_board():
    # High-contrast board: light ivory and slate blue.
    for rank in range(8):
        for file_no in range(8):
            x = BOARD_X + file_no * SQ
            y = BOARD_Y + rank * SQ
            color = LIGHT if (rank + file_no) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (x, y, SQ, SQ))

    # Last move: subtle amber tint, without hiding the square color.
    if board.move_stack:
        last = board.peek()
        for sq in (last.from_square, last.to_square):
            draw_square_overlay(sq, LAST, 85)

    # Selected piece: bright teal border and a light tint.
    if selected_square is not None:
        draw_square_overlay(selected_square, SELECT, 75)
        pygame.draw.rect(screen, (0, 235, 210), square_rect(selected_square), 5)

    # Legal destinations: clear dots; captures use a ring around the piece.
    for target in legal_targets:
        rect = square_rect(target)
        if board.piece_at(target):
            pygame.draw.circle(screen, (15, 135, 105), rect.center, int(SQ*0.39), 5)
        else:
            pygame.draw.circle(screen, (15, 135, 105), rect.center, int(SQ*0.105))
            pygame.draw.circle(screen, (235, 255, 248), rect.center, int(SQ*0.105), 2)

    # Pieces are drawn as vector shapes, not font glyphs.
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            rect = square_rect(square)
            draw_piece(screen, piece, rect.center, SQ)

    # Thin board frame and coordinates.
    pygame.draw.rect(screen, (35, 45, 58),
                     (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), 3)
    for file_no in range(8):
        letter = chr(ord("a") + file_no)
        x = BOARD_X + file_no * SQ + SQ - 18
        y = BOARD_Y + BOARD_SIZE - 20
        draw_text(screen, letter, SMALL, (45, 55, 68), x, y)
    for rank in range(8):
        number = str(8-rank)
        x = BOARD_X + 4
        y = BOARD_Y + rank * SQ + 3
        draw_text(screen, number, SMALL, (45, 55, 68), x, y)


def draw_panel():
    pygame.draw.rect(screen, PANEL, (PANEL_X, 45, 260, 680), border_radius=14)
    draw_text(screen, "2D CHESS", TITLE, (255, 255, 255), PANEL_X+22, 68)
    draw_text(screen, "Python + Pygame", SMALL, (190, 205, 220), PANEL_X+24, 108)

    status = current_status()
    draw_text(screen, status, FONT, (255, 220, 125), PANEL_X+20, 150)

    turn_text = "White" if board.turn else "Black"
    draw_text(screen, "Turn: " + turn_text, FONT, (240, 240, 240), PANEL_X+20, 188)
    draw_text(screen, "MOVE HISTORY", FONT, (255, 255, 255), PANEL_X+20, 235)

    # Move history list
    moves = []
    temp = chess.Board()
    for idx, move in enumerate(board.move_stack):
        san = temp.san(move)
        if idx % 2 == 0:
            moves.append(f"{idx//2+1}. {san}")
        else:
            moves[-1] += f"   {san}"
        temp.push(move)

    visible = moves[scroll_offset:scroll_offset+15]
    for i, item in enumerate(visible):
        draw_text(screen, item, SMALL, (225, 230, 235), PANEL_X+22, 275+i*23)

    # Buttons
    buttons = [
        (pygame.Rect(PANEL_X+18, 630, 105, 38), "UNDO"),
        (pygame.Rect(PANEL_X+137, 630, 105, 38), "RESTART"),
    ]
    for rect, label in buttons:
        pygame.draw.rect(screen, (77, 111, 145), rect, border_radius=8)
        label_img = FONT.render(label, True, (255,255,255))
        screen.blit(label_img, label_img.get_rect(center=rect.center))

    draw_text(screen, "Teal dots = legal moves", SMALL, (150, 230, 210), PANEL_X+18, 686)
    draw_text(screen, "Amber = last move", SMALL, (245, 210, 145), PANEL_X+18, 705)


def board_square_from_mouse(pos):
    x, y = pos
    if not (BOARD_X <= x < BOARD_X+BOARD_SIZE and BOARD_Y <= y < BOARD_Y+BOARD_SIZE):
        return None
    file_no = (x-BOARD_X)//SQ
    rank_no = 7-((y-BOARD_Y)//SQ)
    return chess.square(file_no, rank_no)


def choose_promotion(move):
    # Simple on-screen promotion selector; default to queen if user presses Escape.
    choices = [
        (chess.QUEEN, "Queen", "q"),
        (chess.ROOK, "Rook", "r"),
        (chess.BISHOP, "Bishop", "b"),
        (chess.KNIGHT, "Knight", "n"),
    ]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0,0))
    box = pygame.Rect(260, 300, 480, 150)
    pygame.draw.rect(screen, (43,53,66), box, border_radius=14)
    draw_text(screen, "Choose promotion", TITLE, (255,255,255), 385, 315)
    rects = []
    for i, (piece_type, name, key) in enumerate(choices):
        r = pygame.Rect(285+i*110, 375, 95, 48)
        pygame.draw.rect(screen, (77,111,145), r, border_radius=8)
        label = FONT.render(name, True, (255,255,255))
        screen.blit(label, label.get_rect(center=r.center))
        rects.append((r, piece_type))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, piece_type in rects:
                    if rect.collidepoint(event.pos):
                        return chess.Move(move.from_square, move.to_square, promotion=piece_type)
        clock.tick(30)


def handle_square_click(square):
    global selected_square, legal_targets, message
    if square is None or board.is_game_over():
        return

    piece = board.piece_at(square)
    if selected_square is None:
        if piece and piece.color == board.turn:
            selected_square = square
            legal_targets = [m.to_square for m in board.legal_moves if m.from_square == square]
        return

    candidates = [
        m for m in board.legal_moves
        if m.from_square == selected_square and m.to_square == square
    ]
    if candidates:
        move = candidates[0]
        if any(m.promotion for m in candidates):
            move = choose_promotion(move)
            if move is None:
                return
        move_history.append(board.fen())
        board.push(move)
        message = current_status()
        selected_square = None
        legal_targets = []
    elif piece and piece.color == board.turn:
        selected_square = square
        legal_targets = [m.to_square for m in board.legal_moves if m.from_square == square]
    else:
        selected_square = None
        legal_targets = []


while running:
    clock.tick(60)
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            undo_rect = pygame.Rect(PANEL_X+18, 630, 105, 38)
            restart_rect = pygame.Rect(PANEL_X+137, 630, 105, 38)

            if undo_rect.collidepoint(pos):
                if board.move_stack:
                    board.pop()
                selected_square = None
                legal_targets = []
            elif restart_rect.collidepoint(pos):
                board.reset()
                selected_square = None
                legal_targets = []
                scroll_offset = 0
            else:
                handle_square_click(board_square_from_mouse(pos))

        elif event.type == pygame.MOUSEWHEEL:
            scroll_offset = max(0, min(max(0, len(board.move_stack)//2-14), scroll_offset-event.y))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_u and board.move_stack:
                board.pop()
                selected_square = None
                legal_targets = []
            elif event.key == pygame.K_r:
                board.reset()
                selected_square = None
                legal_targets = []

    draw_board()
    draw_panel()
    pygame.display.flip()

pygame.quit()
sys.exit()
