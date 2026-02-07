"""
Displays the High Scores/Leaderboard.
"""
import sys
import pygame
from settings.Constants import (
    WIDTH, HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_PANEL_BG, COLOR_BORDER
)
from settings.Logic import Button
from settings import JsonStats


def show_leaderboard() -> None:
    """Displays the leaderboard screen."""
    pygame.init()
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Arial", 50, bold=True)
    font_header = pygame.font.SysFont("Arial", 25, bold=True)
    font_row = pygame.font.SysFont("Arial", 30)

    center_x = WIDTH // 2
    btn_back = Button(center_x - 100, HEIGHT - 100, 200, 60, "BACK",
                      COLOR_PANEL_BG, action_id="BACK")

    scores = JsonStats.load_leaderboard()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.is_clicked(mouse_pos):
                    running = False

        screen.fill(COLOR_BG)

        # Title
        title = font_title.render("HALL OF FAME", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(center_x, 60)))

        start_y = 140
        if not scores:
            no_data = font_row.render("No games played yet.", True, COLOR_ACCENT)
            screen.blit(no_data, no_data.get_rect(center=(center_x, 300)))
        else:
            # Header
            screen.blit(font_header.render("RANK", True, COLOR_ACCENT), (center_x - 250, start_y))
            screen.blit(font_header.render("NAME", True, COLOR_ACCENT), (center_x - 100, start_y))
            screen.blit(font_header.render("SCORE", True, COLOR_ACCENT), (center_x + 180, start_y))

            # Divider Line
            pygame.draw.line(screen, COLOR_BORDER,
                             (center_x - 260, start_y + 35),
                             (center_x + 260, start_y + 35), 2)

            # Draw Rows
            for i, entry in enumerate(scores):
                y_pos = start_y + 50 + (i * 45)
                row_color = COLOR_TEXT

                # Special colors for top 3
                if i == 0:
                    row_color = (255, 215, 0)  # Gold
                elif i == 1:
                    row_color = (192, 192, 192)  # Silver
                elif i == 2:
                    row_color = (205, 127, 50)  # Bronze

                rank_surf = font_row.render(f"{i + 1}.", True, row_color)
                name_surf = font_row.render(str(entry['name'])[:12], True, row_color)
                score_surf = font_row.render(str(entry['score']), True, row_color)

                screen.blit(rank_surf, (center_x - 230, y_pos))
                screen.blit(name_surf, (center_x - 100, y_pos))
                screen.blit(score_surf, (center_x + 180, y_pos))

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(30)