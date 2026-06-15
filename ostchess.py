import pygame
import chess
import random
import time
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 640, 640
SQ = WIDTH // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OME CHESS ULTRA")

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

font = pygame.font.SysFont(None, 32)

# ---------------- GAME STATE ----------------
menu = True
mode = None  # pvp / ai / lan

board = chess.Board()

white_elo = 1200
black_elo = 1200

drag_piece = None
drag_from = None
drag_pos = None

promotion_data = None

last_move_time = 0
move_delay = 0.15

clock = pygame.time.Clock()

# ---------------- STOCKFISH (optional) ----------------
STOCKFISH_PATH = "stockfish.exe"
use_stockfish = os.path.exists(STOCKFISH_PATH)

# ---------------- PIECES ----------------
piece_map = {
    "P": "assets/pieces/wp.png",
    "R": "assets/pieces/wr.png",
    "N": "assets/pieces/wn.png",
    "B": "assets/pieces/wb.png",
    "Q": "assets/pieces/wq.png",
    "K": "assets/pieces/wk.png",
    "p": "assets/pieces/bp.png",
    "r": "assets/pieces/br.png",
    "n": "assets/pieces/bn.png",
    "b": "assets/pieces/bb.png",
    "q": "assets/pieces/bq.png",
    "k": "assets/pieces/bk.png",
}

images = {k: pygame.transform.scale(pygame.image.load(v), (SQ, SQ))
          for k, v in piece_map.items()}

# ---------------- HELPERS ----------------
def sq_from_mouse(pos):
    x, y = pos
    return chess.square(x // SQ, 7 - y // SQ)

# ---------------- MENU ----------------
def draw_menu():
    screen.fill((20, 20, 20))

    t = font.render("OME CHESS ULTRA", True, (255, 255, 255))
    screen.blit(t, (200, 120))

    screen.blit(font.render("1 - PvP", True, (0, 255, 0)), (260, 260))
    screen.blit(font.render("2 - vs AI", True, (0, 255, 0)), (260, 310))
    screen.blit(font.render("3 - LAN (beta)", True, (0, 255, 0)), (240, 360))

# ---------------- BOARD ----------------
def draw_board():
    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (c*SQ, r*SQ, SQ, SQ))

# ---------------- PIECES ----------------
def draw_pieces():
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)

        if piece:
            if drag_piece and sq == drag_from:
                continue

            c = chess.square_file(sq)
            r = 7 - chess.square_rank(sq)

            screen.blit(images[piece.symbol()], (c*SQ, r*SQ))

    if drag_piece and drag_pos:
        screen.blit(images[drag_piece], (drag_pos[0]-SQ//2, drag_pos[1]-SQ//2))

# ---------------- PROMOTION ----------------
def draw_promotion():
    global promotion_data
    if not promotion_data:
        return

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    opts = ["Q", "R", "B", "N"]

    for i, p in enumerate(opts):
        img = images[p if board.turn else p.lower()]
        x = 160 + i * 80
        y = 280
        screen.blit(img, (x, y))

def handle_promotion_click(pos):
    global promotion_data

    opts = ["Q", "R", "B", "N"]

    for i, p in enumerate(opts):
        rect = pygame.Rect(160 + i*80, 280, SQ, SQ)
        if rect.collidepoint(pos):
            return p

    return None

# ---------------- AI ----------------
def ai_move():
    if mode != "ai":
        return
    if board.turn == chess.BLACK:

        if use_stockfish:
            import subprocess
            proc = subprocess.Popen(
                [STOCKFISH_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            proc.stdin.write(f"position fen {board.fen()}\n")
            proc.stdin.write("go depth 10\n")
            proc.stdin.flush()

        move = random.choice(list(board.legal_moves))
        board.push(move)

# ---------------- ELO ----------------
def update_elo(winner):
    global white_elo, black_elo

    k = 25

    if winner == "white":
        white_elo += k
        black_elo -= k
    else:
        black_elo += k
        white_elo -= k

# ---------------- LOOP ----------------
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # -------- MENU --------
        if menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "pvp"
                    menu = False
                if event.key == pygame.K_2:
                    mode = "ai"
                    menu = False
                if event.key == pygame.K_3:
                    mode = "lan"
                    menu = False
            continue

        # -------- PROMOTION --------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if promotion_data:
                choice = handle_promotion_click(pygame.mouse.get_pos())
                if choice:
                    frm, to = promotion_data
                    promo_map = {
                        "Q": chess.QUEEN,
                        "R": chess.ROOK,
                        "B": chess.BISHOP,
                        "N": chess.KNIGHT
                    }

                    move = chess.Move(frm, to, promotion=promo_map[choice])

                    if move in board.legal_moves:
                        board.push(move)

                    promotion_data = None
                continue

            sq = sq_from_mouse(pygame.mouse.get_pos())
            piece = board.piece_at(sq)

            if piece and piece.color == board.turn:
                drag_piece = piece.symbol()
                drag_from = sq

        if event.type == pygame.MOUSEMOTION:
            if drag_piece:
                drag_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP:

            if drag_piece:

                if time.time() - last_move_time < move_delay:
                    drag_piece = None
                    continue

                to_sq = sq_from_mouse(pygame.mouse.get_pos())

                piece = board.piece_at(drag_from)

                if piece and piece.piece_type == chess.PAWN:
                    if chess.square_rank(to_sq) in [0, 7]:
                        promotion_data = (drag_from, to_sq)
                    else:
                        move = chess.Move(drag_from, to_sq)
                        if move in board.legal_moves:
                            board.push(move)

                else:
                    move = chess.Move(drag_from, to_sq)
                    if move in board.legal_moves:
                        board.push(move)

                drag_piece = None
                drag_from = None
                drag_pos = None

                last_move_time = time.time()

    # -------- DRAW --------
    if menu:
        draw_menu()

    else:
        draw_board()
        draw_pieces()
        draw_promotion()

        ai_move()

        if board.is_checkmate():
            winner = "white" if board.turn == chess.BLACK else "black"
            update_elo(winner)

            txt = font.render("CHECKMATE!", True, (255, 0, 0))
            screen.blit(txt, (240, 300))

        elif board.is_check():
            txt = font.render("CHECK!", True, (255, 0, 0))
            screen.blit(txt, (270, 300))

        screen.blit(font.render(f"W: {white_elo}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(f"B: {black_elo}", True, (0, 0, 0)), (10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()