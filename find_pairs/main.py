import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 900, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Royal Purple — Найди пару или тройку")

FPS = 60

BG_TOP = (31, 17, 58)
BG_BOTTOM = (12, 8, 27)
PURPLE = (73, 39, 112)
PURPLE_LIGHT = (111, 72, 157)
GOLD = (232, 190, 91)
GOLD_LIGHT = (255, 222, 145)
WHITE = (248, 242, 255)
MUTED = (184, 166, 207)
GREEN = (110, 210, 150)
RED = (225, 105, 120)

FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 19)
TITLE_FONT = pygame.font.SysFont("arial", 47, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 34, bold=True)

CLOCK = pygame.time.Clock()

DIFFICULTIES = {
    "pair": {
        "Легко": (4, 4),
        "Средне": (4, 5),
        "Сложно": (4, 6),
    },
    "triple": {
        "Легко": (3, 4),
        "Средне": (4, 6),
        "Сложно": (5, 6),
    }
}

SYMBOLS = [
    "★", "◆", "●", "♠", "♥", "♣",
    "☀", "☾", "✿", "♫", "♦", "♛",
    "⚜", "✦", "☘", "❖", "☯", "✧"
]

mode = "pair"
difficulty = "Легко"

cards = []
revealed = []
matched = set()

moves = 0
start_time = 0
finished = False
waiting_until = None

game_state = "menu"

def draw_background():
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(
            int(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t)
            for i in range(3)
        )
        pygame.draw.line(SCREEN, color, (0, y), (WIDTH, y))

def draw_text(text, font, color, center):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect(center=center)
    SCREEN.blit(surface, rect)
    return rect

def draw_button(rect, text, selected=False):
    color = PURPLE_LIGHT if selected else PURPLE
    pygame.draw.rect(SCREEN, color, rect, border_radius=13)
    pygame.draw.rect(SCREEN, GOLD, rect, 2, border_radius=13)
    draw_text(text, FONT, GOLD_LIGHT if selected else WHITE, rect.center)

def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02}:{secs:02}"

def get_group_size():
    return 2 if mode == "pair" else 3

def get_mode_name():
    return "ПАРЫ" if mode == "pair" else "ТРОЙКИ"

def draw_menu():
    draw_background()

    draw_text("ROYAL PURPLE", TITLE_FONT, GOLD, (WIDTH // 2, 105))
    draw_text("НАЙДИ СОВПАДЕНИЯ", BIG_FONT, WHITE, (WIDTH // 2, 165))

    draw_text("Выбери режим игры", FONT, GOLD_LIGHT, (WIDTH // 2, 245))

    pair_rect = pygame.Rect(210, 285, 220, 65)
    triple_rect = pygame.Rect(470, 285, 220, 65)

    draw_button(pair_rect, "Найти пару", mode == "pair")
    draw_button(triple_rect, "Найти тройку", mode == "triple")

    draw_text("Выбери сложность", FONT, GOLD_LIGHT, (WIDTH // 2, 405))

    easy = pygame.Rect(145, 455, 180, 60)
    medium = pygame.Rect(360, 455, 180, 60)
    hard = pygame.Rect(575, 455, 180, 60)

    draw_button(easy, "Легко", difficulty == "Легко")
    draw_button(medium, "Средне", difficulty == "Средне")
    draw_button(hard, "Сложно", difficulty == "Сложно")

    draw_text(
        "Легко → Средне → Сложно",
        SMALL_FONT,
        MUTED,
        (WIDTH // 2, 555)
    )

    draw_text(
        "Найди все одинаковые символы!",
        SMALL_FONT,
        GOLD,
        (WIDTH // 2, 620)
    )

    return {
        "pair": pair_rect,
        "triple": triple_rect,
        "easy": easy,
        "medium": medium,
        "hard": hard,
    }

def start_game():
    global cards, revealed, matched
    global moves, start_time, finished, waiting_until
    global game_state

    rows, cols = DIFFICULTIES[mode][difficulty]
    group_size = get_group_size()

    total_cards = rows * cols
    group_count = total_cards // group_size

    chosen_symbols = SYMBOLS[:group_count]

    values = []
    for symbol in chosen_symbols:
        values.extend([symbol] * group_size)

    random.shuffle(values)

    cards = values
    revealed = []
    matched = set()

    moves = 0
    start_time = pygame.time.get_ticks()
    finished = False
    waiting_until = None

    game_state = "game"

def get_card_rects():
    rows, cols = DIFFICULTIES[mode][difficulty]

    gap = 12
    max_width = 790
    max_height = 450

    card_width = min(
        (max_width - (cols - 1) * gap) // cols,
        125
    )

    card_height = min(
        (max_height - (rows - 1) * gap) // rows,
        105
    )

    total_width = cols * card_width + (cols - 1) * gap
    total_height = rows * card_height + (rows - 1) * gap

    start_x = (WIDTH - total_width) // 2
    start_y = 205 + (450 - total_height) // 2

    rects = []

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (card_width + gap)
            y = start_y + row * (card_height + gap)
            rects.append(pygame.Rect(x, y, card_width, card_height))

    return rects

def draw_card(rect, index):
    is_open = index in revealed or index in matched

    shadow = rect.move(4, 5)
    pygame.draw.rect(SCREEN, (5, 3, 15), shadow, border_radius=12)

    if is_open:
        pygame.draw.rect(
            SCREEN,
            (93, 65, 128),
            rect,
            border_radius=12
        )
        pygame.draw.rect(
            SCREEN,
            GOLD,
            rect,
            3,
            border_radius=12
        )

        draw_text(
            cards[index],
            BIG_FONT,
            GOLD_LIGHT,
            rect.center
        )

        if index in matched:
            pygame.draw.rect(
                SCREEN,
                GREEN,
                rect,
                3,
                border_radius=12
            )

    else:
        pygame.draw.rect(
            SCREEN,
            PURPLE,
            rect,
            border_radius=12
        )
        pygame.draw.rect(
            SCREEN,
            GOLD,
            rect,
            2,
            border_radius=12
        )

        draw_text("✦", BIG_FONT, GOLD, rect.center)

def draw_game():
    draw_background()

    elapsed = (pygame.time.get_ticks() - start_time) // 1000

    total_groups = len(cards) // get_group_size()
    found_groups = len(matched) // get_group_size()

    draw_text("ROYAL PURPLE", TITLE_FONT, GOLD, (WIDTH // 2, 55))

    draw_text(
        f"Режим: {get_mode_name()}",
        FONT,
        WHITE,
        (WIDTH // 2, 115)
    )

    draw_text(
        f"Сложность: {difficulty}",
        SMALL_FONT,
        MUTED,
        (WIDTH // 2, 150)
    )

    draw_text(
        f"Ходы: {moves}",
        SMALL_FONT,
        GOLD_LIGHT,
        (170, 180)
    )

    draw_text(
        f"Время: {format_time(elapsed)}",
        SMALL_FONT,
        GOLD_LIGHT,
        (WIDTH // 2, 180)
    )

    draw_text(
        f"{get_mode_name()}: {found_groups}/{total_groups}",
        SMALL_FONT,
        GOLD_LIGHT,
        (730, 180)
    )

    for i, rect in enumerate(get_card_rects()):
        draw_card(rect, i)

    back_rect = pygame.Rect(20, 20, 125, 42)
    draw_button(back_rect, "В меню")

    if finished:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        SCREEN.blit(overlay, (0, 0))

        draw_text("ПОБЕДА!", TITLE_FONT, GOLD, (WIDTH // 2, 270))
        draw_text(
            f"Ты нашёл все {get_mode_name().lower()}!",
            FONT,
            WHITE,
            (WIDTH // 2, 335)
        )
        draw_text(
            f"Ходы: {moves}   Время: {format_time(elapsed)}",
            FONT,
            GOLD_LIGHT,
            (WIDTH // 2, 390)
        )

        draw_text(
            "Нажми ENTER, чтобы сыграть снова",
            SMALL_FONT,
            WHITE,
            (WIDTH // 2, 465)
        )

        draw_text(
            "Нажми ESC, чтобы вернуться в меню",
            SMALL_FONT,
            MUTED,
            (WIDTH // 2, 505)
        )

    return back_rect

def check_selection():
    global moves, waiting_until, finished

    group_size = get_group_size()

    if len(revealed) != group_size:
        return

    moves += 1

    selected_values = [cards[i] for i in revealed]

    if len(set(selected_values)) == 1:
        matched.update(revealed)
        revealed.clear()

        if len(matched) == len(cards):
            finished = True

    else:
        waiting_until = pygame.time.get_ticks() + 950

def handle_card_click(pos):
    global waiting_until

    if finished or waiting_until is not None:
        return

    for index, rect in enumerate(get_card_rects()):
        if rect.collidepoint(pos):
            if index in matched or index in revealed:
                return

            revealed.append(index)

            if len(revealed) == get_group_size():
                check_selection()

            return

def update_game():
    global revealed, waiting_until

    if waiting_until is not None:
        if pygame.time.get_ticks() >= waiting_until:
            revealed.clear()
            waiting_until = None

def main():
    global game_state, mode, difficulty

    running = True

    while running:
        CLOCK.tick(FPS)

        if game_state == "menu":
            buttons = draw_menu()
        else:
            back_rect = draw_game()
            update_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "game":
                        game_state = "menu"

                if game_state == "game" and finished:
                    if event.key == pygame.K_RETURN:
                        start_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue

                if game_state == "menu":
                    if buttons["pair"].collidepoint(event.pos):
                        mode = "pair"

                    elif buttons["triple"].collidepoint(event.pos):
                        mode = "triple"

                    elif buttons["easy"].collidepoint(event.pos):
                        difficulty = "Легко"
                        start_game()

                    elif buttons["medium"].collidepoint(event.pos):
                        difficulty = "Средне"
                        start_game()

                    elif buttons["hard"].collidepoint(event.pos):
                        difficulty = "Сложно"
                        start_game()

                elif game_state == "game":
                    if back_rect.collidepoint(event.pos):
                        game_state = "menu"
                    else:
                        handle_card_click(event.pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()