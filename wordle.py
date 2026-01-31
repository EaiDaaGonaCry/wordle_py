import pygame
import sys
from Modes import AiMode, PlayerMode
from Settings.Constants import *

pygame.init()

WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle")

HOVER_COLOR = COLOR_BORDER

FONT_TITLE = pygame.font.SysFont("Arial", 80, bold=True)
FONT_BUTTON = pygame.font.SysFont("Arial", 40)


class Button:
    def __init__(self, text, x, y, width, height, action_id):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action_id = action_id
        self.is_hovered = False

    def draw(self, screen):
        color = HOVER_COLOR if self.is_hovered else COLOR_PANEL_BG

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, 2, border_radius=10)  # Border

        text_surf = FONT_BUTTON.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return self.action_id
        return None


def main_menu():
    btn_width, btn_height = 400, 80
    center_x = (WIDTH - btn_width) // 2

    btn_play   = Button("Play Wordle", center_x, 300, btn_width, btn_height, "PLAY")
    btn_solver = Button("Wordle Solver", center_x, 400, btn_width, btn_height, "SOLVER")
    btn_quit   = Button("Quit Game", center_x, 500, btn_width, btn_height, "EXIT")

    buttons = [btn_play, btn_solver, btn_quit]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    action = btn.check_click(mouse_pos)

                    if action == "PLAY":
                        # 1. Call the function inside PlayerMode
                        difficulty = PlayerMode.select_difficulty()

                        # 2. Check the result
                        if difficulty == "QUIT":
                            pygame.quit()
                            sys.exit()

                        elif difficulty == "BACK":
                            # Just do nothing, loop continues and redraws main menu
                            pass

                        else:
                            # 3. If "NORMAL" or "EXTREME", start the game loop
                            current_state = "RESTART"
                            while current_state == "RESTART":
                                # Pass the difficulty we selected earlier
                                current_state = PlayerMode.run_game(difficulty)

                            if current_state == "QUIT":
                                pygame.quit()
                                sys.exit()

                            pygame.display.set_caption("Wordle")

                    elif action == "SOLVER":
                        current_state = "RESTART"

                        while current_state == "RESTART":
                            current_state = AiMode.run_ai_mode()

                        if current_state == "QUIT":
                            pygame.quit()
                            sys.exit()

                        pygame.display.set_caption("Wordle")

                    elif action == "EXIT":
                        pygame.quit()
                        sys.exit()

        SCREEN.fill(COLOR_BG)

        title_surf = FONT_TITLE.render("WORDLE MASTER", True, COLOR_CORRECT)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 150))
        SCREEN.blit(title_surf, title_rect)

        for btn in buttons:
            btn.check_hover(mouse_pos)
            btn.draw(SCREEN)

        pygame.display.flip()


if __name__ == "__main__":
    main_menu()