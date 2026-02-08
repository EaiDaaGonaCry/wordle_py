"""
Difficulty Menu Module.
Handles the UI for selecting game difficulty.
"""
import sys
from typing import Optional, List, Tuple
import pygame

from settings.Logic import Button
from settings.Constants import (
    WIDTH, HEIGHT, COLOR_BG, COLOR_TEXT, COLOR_PANEL_BG,
    COLOR_CORRECT, COLOR_RED, COLOR_ABSENT, COLOR_ABSENT_BORDER
)


def get_difficulty() -> Optional[str]:
    """
    Runs a standalone loop for difficulty selection.
    Returns: "NORMAL", "EXTREME", or None (if closed/cancelled).
    """
    screen: pygame.Surface = pygame.display.get_surface()

    # --- Layout Configuration ---
    panel_w: int = 500
    panel_h: int = 400
    btn_w: int = 300
    btn_h: int = 80
    gap: int = 20

    # Center points
    center_x: int = WIDTH // 2
    center_y: int = HEIGHT // 2
    start_btn_y: int = center_y - 20

    # Fonts
    title_font: pygame.font.Font = pygame.font.SysFont("Arial", 40, bold=True)

    # --- Create Buttons ---
    btn_normal = Button(center_x - btn_w // 2, start_btn_y, btn_w, btn_h, "NORMAL",
                        color=COLOR_PANEL_BG,
                        hover_color=COLOR_CORRECT,
                        border_color=COLOR_ABSENT_BORDER,
                        action_id="NORMAL")

    btn_extreme = Button(center_x - btn_w // 2, start_btn_y + btn_h + gap, btn_w, btn_h, "EXTREME",
                         color=COLOR_PANEL_BG,
                         hover_color=COLOR_RED,
                         border_color=COLOR_ABSENT_BORDER,
                         action_id="EXTREME")

    btn_back = Button(center_x - btn_w // 2, start_btn_y + 2 * (btn_h + gap), btn_w, btn_h, "BACK",
                      color=COLOR_PANEL_BG,
                      hover_color=COLOR_ABSENT,
                      border_color=COLOR_ABSENT_BORDER,
                      action_id="BACK")

    buttons: List[Button] = [btn_normal, btn_extreme, btn_back]

    # --- Menu Loop ---
    running: bool = True

    while running:
        mouse_pos: Tuple[int, int] = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    if btn.is_clicked(mouse_pos):
                        if btn.action_id == "BACK":
                            return None
                        return btn.action_id

        # --- Drawing ---
        screen.fill(COLOR_BG)

        # Title
        title_surf: pygame.Surface = title_font.render("SELECT DIFFICULTY", True, COLOR_TEXT)
        title_rect: pygame.Rect = title_surf.get_rect(center=(center_x, center_y - 100))
        screen.blit(title_surf, title_rect)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return None