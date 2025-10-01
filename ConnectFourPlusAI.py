import math
import random
import sys
import numpy as np
import pygame

BLUE = (0, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)

ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def winning_move(board, piece):
    # Горизонтальна перевірка
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if piece == board[r][c] == board[r][c + 1] == board[r][c + 2] == board[r][c + 3]:
                return True

    # Вертикальна перевірка
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if piece == board[r][c] ==  board[r + 1][c] == board[r + 2][c] == board[r + 3][c]:
                return True

    # Діагональна перевірка (зліва направо вгору)
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if piece == board[r][c] == board[r + 1][c + 1] == board[r + 2][c + 2] == board[r + 3][c + 3]:
                return True

    # Діагональна перевірка (зліва направо вниз)
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if piece == board[r][c] == board[r - 1][c + 1] ==board[r - 2][c + 2] == board[r - 3][c + 3]:
                return True

    return False


def evaluate_window(window, piece):
    score = 0
    opp_piece = AI_PIECE if piece == PLAYER_PIECE else PLAYER_PIECE

    if window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Вертикальний рахунок
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Позитивний діагональний рахунок
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Негативний діагональний рахунок
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


def is_terminal_node(board):
    return (winning_move(board, PLAYER_PIECE) or
            winning_move(board, AI_PIECE) or
            len(get_valid_locations(board)) == 0)


def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, math.inf
            elif winning_move(board, PLAYER_PIECE):
                return None, -math.inf
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PIECE)

    if maximizing_player:
        value = -math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def draw_board(board, screen):
    height = (ROW_COUNT + 1) * SQUARESIZE

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK,
                               (int(c * SQUARESIZE + SQUARESIZE / 2),
                                int(r * SQUARESIZE + 1.5 * SQUARESIZE)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + 0.5 * SQUARESIZE)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW,
                                   (int(c * SQUARESIZE + SQUARESIZE / 2),
                                    height - int(r * SQUARESIZE + 0.5 * SQUARESIZE)), RADIUS)
    pygame.display.update()

def initial_screen(width, height):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Starting menu")


    font_title = pygame.font.Font(None, 36)
    font_text = pygame.font.Font(None, 28)
    font_button = pygame.font.Font(None, 24)

    turn = None
    depth = None
    step = 1

    while turn is None or depth is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                if step == 1:
                    if 150 <= mouse_x <= 300 and 200 <= mouse_y <= 240:
                        turn = 0
                        step = 2

                    elif 400 <= mouse_x <= 550 and 200 <= mouse_y <= 240:
                        turn = 1
                        step = 2

                elif step == 2:
                    for i in range(6):
                        button_x = 100 + i * 80
                        if button_x <= mouse_x <= button_x + 60 and 200 <= mouse_y <= 240:
                            depth = i + 1
                            break

        screen.fill(WHITE)

        if step == 1:
            title_text = font_title.render("Хто ходить першим?", True, BLACK)
            title_rect = title_text.get_rect(center=(width // 2, 100))
            screen.blit(title_text, title_rect)

            player_button = pygame.Rect(150, 200, 150, 40)
            pygame.draw.rect(screen, RED, player_button)
            pygame.draw.rect(screen, BLACK, player_button, 2)

            player_text = font_button.render("Гравець", True, WHITE)
            player_text_rect = player_text.get_rect(center=player_button.center)
            screen.blit(player_text, player_text_rect)

            ai_button = pygame.Rect(400, 200, 150, 40)
            pygame.draw.rect(screen, YELLOW, ai_button)
            pygame.draw.rect(screen, BLACK, ai_button, 2)

            ai_text = font_button.render("Штучний інтелект", True, WHITE)
            ai_text_rect = ai_text.get_rect(center=ai_button.center)
            screen.blit(ai_text, ai_text_rect)

        elif step == 2:
            title_text = font_title.render("Виберіть рівень складності:", True, BLACK)
            title_rect = title_text.get_rect(center=(width // 2, 100))
            screen.blit(title_text, title_rect)

            turn_text = font_text.render(f"Першим ходить: {'Гравець' if turn == 0 else 'ШІ'}", True, BLACK)
            turn_rect = turn_text.get_rect(center=(width // 2, 140))
            screen.blit(turn_text, turn_rect)

            for i in range(6):
                button_x = 100 + i * 80
                difficulty_button = pygame.Rect(button_x, 200, 60, 40)
                pygame.draw.rect(screen, ORANGE, difficulty_button)
                pygame.draw.rect(screen, BLACK, difficulty_button, 2)

                level_text = font_button.render(str(i + 1), True, WHITE)
                level_text_rect = level_text.get_rect(center=difficulty_button.center)
                screen.blit(level_text, level_text_rect)

            hint_text = font_text.render("1 - легко, 6 - дуже важко", True, PURPLE)
            hint_rect = hint_text.get_rect(center=(width // 2, 280))
            screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    pygame.quit()
    return turn, depth


def last_screen():
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 20000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.delay(100)

def main():
    board = create_board()
    game_over = False

    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE
    size = (width, height)
    turn, depth = initial_screen(width, height)

    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect Four")
    draw_board(board, screen)

    myfont = pygame.font.SysFont("corbel", 75)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                if turn == PLAYER:
                    col = event.pos[0] // SQUARESIZE

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (50, 10))
                            game_over = True

                        turn = (turn + 1) % 2
                        draw_board(board, screen)

        if turn == AI and not game_over:
            col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("Player 2 wins!!", 1, YELLOW)
                    screen.blit(label, (50, 10))
                    game_over = True

                draw_board(board, screen)
                turn = (turn + 1) % 2

        if game_over:
            last_screen()


if __name__ == "__main__":
    main()
    pygame.font.get_fonts()